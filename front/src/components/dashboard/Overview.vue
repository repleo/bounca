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
              <v-toolbar-title>Certificates</v-toolbar-title>
            </v-toolbar>
            <v-toolbar
              flat
            >
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
          <template v-slot:[`item.name`]="{ item }">
            <v-btn
              :disabled="item.revoked || item.expired"
              class="ma-1"
              color="blue darken-2"
              plain
              v-if="item.type == 'R'"
              @click="selectRootCertificate(item)"
            >
              {{ item.name }}
            </v-btn>
            <v-btn
              :disabled="item.revoked || item.expired"
              class="ma-1"
              color="blue darken-2"
              plain
              v-if="item.type == 'I'"
              @click="selectIntermediateCertificate(item)"
            >
              {{ item.name }}
            </v-btn>
            <div
              class="text-button ml-5 blue-grey--text"
              v-if="!(item.type == 'I' | item.type == 'R')"
            >
              {{ item.name }}
            </div>
           </template>
                    <template v-slot:[`item.type`]="{item}">
            <span v-if="item.type == 'R'" class="">
              Root
            </span>
            <span v-if="item.type == 'I'" class="">
              Intermediate
            </span>
            <span v-if="item.type == 'S'" class="">
              Server
            </span>
            <span v-if="item.type == 'C'" class="">
              Client
            </span>
            <span v-if="item.type == 'O'" class="">
              OCSP
            </span>
          </template>
          <template v-slot:[`item.actions`]="{ item }">
            <span v-if="item.revoked" class="font-weight-bold red--text">
              REVOKED
            </span>
            <span v-else-if="item.expired" class="mr-2 font-weight-bold blue--text">
              EXPIRED
            </span>
            <span v-else>
              <v-icon class="mr-2" color="red darken-2" @click="revokeCertificate(item.id)">
                mdi-delete
              </v-icon>
              <v-icon class="mr-2" color="blue darken-2" @click="infoCertificate(item.id)">
                mdi-information
              </v-icon>
              <v-icon class="mr-2" color="grey darken-2"
                      @click="downloadCertificate(item.id)">
                mdi-download
              </v-icon>
            </span>
          </template>
        </v-data-table>
      </v-card>
    </v-col>
  </v-row>

  <v-dialog v-model="dialogDelete" max-width="565px">
    <v-card>
      <v-card-title class="text-h5">Are you sure you want to
        revoke this certificate?</v-card-title>
      <v-card-text>
          <ValidationObserver ref="form" v-slot="{ errors }">
          <ValidationProvider name="non_field_errors" vid="non_field_errors">
            <v-alert
              text
              dense
              type="error"
              border="left"
              v-if="errors.non_field_errors && errors.non_field_errors.length"
            >
            <div v-for="error in errors.non_field_errors" :key="error">{{error}}</div>
            </v-alert>
          </ValidationProvider>
          <v-form>
            <ValidationProvider name="passphrase_issuer" vid="passphrase_issuer" rules="required"
                                v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="passphrase"
              label="Passphrase"
              id="passphrase"
              v-model="revoke.passphrase_issuer"
              :error-messages="errors"
              :append-icon="revoke_passphrase_visible ? 'visibility' : 'visibility_off'"
              @click:append="() => (revoke_passphrase_visible = !revoke_passphrase_visible)"
              :type="revoke_passphrase_visible ? 'text' : 'password' "
              required
            ></v-text-field>
            </ValidationProvider>
          </v-form>
          </ValidationObserver>
        </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="closeRevoke">Cancel</v-btn>
        <v-btn color="blue darken-1" text
               @click="revokeCertificateConfirm">OK</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="dialogDownloading" max-width="565px">
    <v-card >
      <v-container style="height: 200px;">
        <v-row
          class="fill-height"
          align-content="center"
          justify="center"
        >
          <v-col
            class="text-subtitle-1 text-center"
            cols="12"
          >
            Getting your files
          </v-col>
          <v-col cols="6">
            <v-progress-linear
              color="deep-purple accent-4"
              indeterminate
              rounded
              height="6"
            ></v-progress-linear>
          </v-col>
        </v-row>
      </v-container>
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
  <v-dialog v-model="dialogError" width="800px">
    <v-card>
      <v-card-title class="text-h5">Error</v-card-title>
      <v-card-text>
            <v-alert
      border="right"
      colored-border
      type="error"
      elevation="2"
            >
              {{ dialogErrorText }}
            </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
          <v-btn
            color="blue darken-2"
            text
            @click="dialogError = false"
          >
            Close
          </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  </v-container>
</template>

<script>
import { mapMutations } from 'vuex';
import certificates from '../../api/certificates';

export default {
  name: 'DashboardOverview',
  data() {
    return {
      revoke: {
        passphrase_issuer: null,
      },
      revoke_passphrase_visible: false,
      dialogDownloading: false,
      dialogDelete: false,
      deleteItem: null,
      dialogInfo: false,
      dialogInfoText: '',
      dialogInfoLoading: true,

      dialogError: false,
      dialogErrorText: '',

      loading: true,
      items_per_page_selector: [10, 25, 50],
      pagination: {},
      certificates: [],
      filter: '',
      headers: [
        {
          text: 'Name', align: 'start', sortable: true, value: 'name',
        },
        {
          text: 'Type', value: 'type', sortable: true,
        },
        {
          text: 'Common Name', value: 'commonName', sortable: true,
        },
        {
          text: 'Email Address', value: 'emailAddress', sortable: true,
        },
        {
          text: 'Expires At', value: 'expiresAt', sortable: true,
        },
        {
          text: 'Actions', value: 'actions', sortable: false,
        },
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
        this.closeRevoke();
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
    ...mapMutations('dashboard', ['setRoot', 'setIntermediate']),
    getRequestParams(filter, pagination) {
      const params = { };
      if ('sortBy' in pagination && pagination.sortBy.length === 1
        && 'sortDesc' in pagination && pagination.sortDesc.length === 1) {
        if (pagination.sortBy[0] === 'expiresAt') {
          params.ordering = 'expires_at';
        } else if (pagination.sortBy[0] === 'commonName') {
          params.ordering = 'dn__commonName';
        } else if (pagination.sortBy[0] === 'emailAddress') {
          params.ordering = 'dn__emailAddress';
        } else {
          const [sortBy] = pagination.sortBy;
          params.ordering = sortBy;
        }
        if (pagination.sortDesc[0]) {
          params.ordering = `-${params.ordering}`;
        }
      } else {
        params.ordering = '-id';
      }

      if (filter) {
        params.search = filter;
      }

      if ('page' in pagination && pagination.page) {
        params.page = pagination.page;
      }

      if ('itemsPerPage' in pagination && pagination.itemsPerPage) {
        params.page_size = pagination.itemsPerPage;
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
          const { count, results } = response;
          this.certificates = results.map(this.getDisplayCertificate);
          this.totalCertificates = count;
        })
        .catch((e) => {
          this.dialogErrorText = e;
          this.dialogError = true;
        });
    },

    getDisplayCertificate(certificate) {
      return {
        id: certificate.id,
        name: certificate.name,
        type: certificate.type,
        commonName: certificate.dn.commonName,
        emailAddress: certificate.dn.emailAddress,
        expiresAt: certificate.expires_at,
        revoked: certificate.revoked,
        expired: certificate.expired,
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
          this.dialogInfoLoading = false;
          this.dialogInfoText = `No data, please check your certificate. Error: ${e}`;
        });
    },

    downloadCertificateFinished() {
      this.dialogDownloading = false;
    },

    downloadCertificateError(e) {
      this.dialogDownloading = false;
      this.dialogErrorText = e;
      this.dialogError = true;
    },

    downloadCertificate(item) {
      this.dialogDownloading = true;
      certificates.downloadCertificate(
        item,
        this.downloadCertificateFinished,
        this.downloadCertificateError,
      );
    },

    revokeCertificate(item) {
      this.deleteItem = item;
      this.dialogDelete = true;
    },

    revokeCertificateConfirm() {
      if (this.deleteItem !== null) {
        certificates.revoke(this.deleteItem, this.revoke)
          .then(() => {
            this.updateDashboard();
            this.closeRevoke();
          }).catch((r) => {
            const errors = r.response.data;
            this.$refs.form.setErrors(errors);
          });
      }
    },

    closeRevoke() {
      this.revoke.passphrase_issuer = '';
      this.$refs.form.reset();
      this.dialogDelete = false;
      this.deleteItem = null;
    },

    closeInfo() {
      this.dialogInfo = false;
    },

    updateDashboard() {
      this.retrieveCertificates();
    },

    selectRootCertificate(item) {
      this.$router.push(`/dashboard/intermediate/${item.id}`);
    },
    selectIntermediateCertificate(item) {
      this.$router.push(`/dashboard/certificate/${item.id}`);
    },
  },
  mounted() {
    this.setRoot({ id: null, name: '', active: false });
    this.setIntermediate({ id: null, name: '', active: false });
    this.updateDashboard();
  },
};
</script>
