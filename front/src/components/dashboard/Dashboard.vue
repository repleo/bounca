<template>
  <v-container fluid>
   <v-row align="center" class="list px-3 mx-auto">


    <v-col cols="12" sm="12">
      <v-card class="mx-auto" tile>
        <v-data-table
          :headers="headers"
          :items="certificates"
          :options.sync="pagination"
          :server-items-length="totalCertificates"
          :loading="loading"
          :page.sync="page"
          class="elevation-1"
          :footer-props="{'items-per-page options': items_per_page_selector}"
        >
          <template v-slot:top>
            <v-toolbar
              flat
            >
              <v-toolbar-title>Root Certificates</v-toolbar-title>
            </v-toolbar>
            <v-toolbar
              flat
            >
              <v-btn
                color="primary"
                dark
                class="mb-2"
                @click='dialog = !dialog'
              >
                New Certficate
              </v-btn>
              <v-spacer></v-spacer>
              <v-col cols="4" sm="4">
                <v-text-field
                  v-model="filter"
                  @input="page = 1; updateDashboard();"
                  append-icon="mdi-magnify"
                  label="Search"
                  single-line
                  hide-details
                ></v-text-field>
              </v-col>
            </v-toolbar>
          </template>
          <template v-slot:[`item.actions`]="{ item }">
            <!-- TODO: add logic for revoked & expired certificates -->
            <v-icon class="mr-2" color="red darken-2" @click="revokeCertificate(item.id)">
              mdi-delete
            </v-icon>
            <v-icon class="mr-2" color="blue darken-2" @click="infoCertificate(item.id)">
              mdi-information
            </v-icon>
            <v-icon class="mr-2" color="grey darken-2" @click="downloadCertificate(item.id)">
              mdi-download
            </v-icon>
          </template>
        </v-data-table>
      </v-card>
    </v-col>
  </v-row>

  <v-dialog v-model='dialog' width='800px'>
    <forms-RootCert v-on:close-dialog="closeDialog"
                    v-on:update-dasboard="updateDashboard" ref="rootCertForm"/>
  </v-dialog>
  <v-dialog v-model="dialogDelete" max-width="600px">
    <v-card>
      <v-card-title class="text-h5">Are you sure you want to
        revoke this certificate?</v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
        <v-btn color="blue darken-1" text
               @click="revokeCertificateConfirm">OK</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
    <v-dialog v-model="dialogInfo" width="800px">
    <v-card :loading="dialogInfoLoading">
      <v-card-title class="text-h5">Certificate info</v-card-title>
      <v-divider class="mx-4"></v-divider>
      <v-card-text>
        <pre style="white-space: pre-wrap"><div v-html="dialogInfoText"></div></pre>
      </v-card-text>
      <v-divider class="mx-4"></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
          <v-btn
            color="blue darken-2"
            text
            @click="dialogInfo = false"
          >
            Close
          </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  </v-container>
</template>

<script>
import certificates from '../../api/certificates';


export default {
  name: 'Dashboard',
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      dialogInfo: false,
      dialogInfoText: '',
      dialogInfoLoading: true,
      loading: true,
      items_per_page_selector: [10, 25, 50],
      pagination: {},
      certificates: [],
      filter: '',
      headers: [
        { text: 'Name', align: 'start', sortable: true, value: 'name' },
        { text: 'Common Name', value: 'commonName', sortable: true },
        { text: 'Email Address', value: 'emailAddress', sortable: true },
        { text: 'Expires At', value: 'expiresAt', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false },
      ],
      page: 1,
      totalCertificates: 0,
    };
  },
  watch: {
    dialog(val) {
      if (!val) {
        this.$refs.rootCertForm.resetForm();
      }
    },
    dialogDelete(val) {
      if (!val) {
        this.closeDelete();
      }
    },
    dialogInfo(val) {
      if (!val) {
        this.closeInfo();
      }
    },
    pagination: {
      handler() {
        this.updateDashboard();
      },
      deep: true,
    },
  },
  methods: {
    getRequestParams(filter, pagination) {
      const params = { type: 'R' };
      const { sortBy, sortDesc, page, itemsPerPage } = pagination;

      if (sortBy.length === 1 && sortDesc.length === 1) {
        if (sortBy[0] === 'expiresAt') {
          params.ordering = 'expires_at';
        } else if (sortBy[0] === 'commonName') {
          params.ordering = 'dn__commonName';
        } else if (sortBy[0] === 'emailAddress') {
          params.ordering = 'dn__emailAddress';
        } else {
          params.ordering = sortBy[0];
        }
        if (sortDesc[0]) {
          params.ordering = `-${params.ordering}`;
        }
      }

      if (filter) {
        params.search = filter;
      }

      if (page) {
        params.page = page;
      }

      if (itemsPerPage) {
        params.page_size = itemsPerPage;
      }

      return params;
    },

    retrieveCertificates() {
      const params = this.getRequestParams(
        this.filter,
        this.pagination,
      );
      this.loading = true;
      certificates.getAll(params)
        .then((response) => {
          this.loading = false;
          const count = response.count;
          const results = response.results;
          this.certificates = results.map(this.getDisplayCertificate);
          this.totalCertificates = count;
        })
        .catch((e) => {
          console.log(e);
        });
    },

    getDisplayCertificate(certificate) {
      return {
        id: certificate.id,
        name: certificate.name,
        commonName: certificate.dn.commonName,
        emailAddress: certificate.dn.emailAddress,
        expiresAt: certificate.expires_at,
      };
    },

    infoCertificate(item) {
      this.dialogInfoText = '';
      this.dialogInfoLoading = true;
      this.dialogInfo = true;
      certificates.getInfo(item)
        .then((response) => {
          this.dialogInfoLoading = false;
          this.dialogInfoText = response.text;
        })
        .catch((e) => {
          console.log(e);
          this.dialogInfoLoading = false;
          this.dialogInfoText = 'No data, please check your certificate';
        });
    },

    revokeCertificate(item) {
      this.dialogDelete = true;
      console.log(item);
    },

    revokeCertificateConfirm() {
      this.closeDelete();
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        console.log('FUBAR BJA');
        // this.editedItem = Object.assign({}, this.defaultItem);
        // this.editedIndex = -1;
      });
    },

    closeInfo() {
      this.dialogInfo = false;
    },

    updateDashboard() {
      this.retrieveCertificates();
    },
    closeDialog() {
      this.dialog = false;
    },
  },
  mounted() {
    this.updateDashboard();
  },
};
</script>
