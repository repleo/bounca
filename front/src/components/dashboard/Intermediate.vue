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
              <v-toolbar-title>
                Intermediate Certificates for parent {{ parentCertificate.name }}
        (
 <span v-if="parentCertificate.revoked" class="font-weight-bold red--text">REVOKED</span>
 <span v-else-if="parentCertificate.expired" class="font-weight-bold red--text">EXPIRED</span>
        )
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <v-switch
                v-model="displayRevoked"
                label="Display Revoked"
                class="mt-2"
                @change="updateDashboard();"
              ></v-switch>
            </v-toolbar>
            <v-toolbar
              flat
            >
              <v-btn
                color="primary"
                dark
                class="mb-2"
                @click='dialog = !dialog'
                v-if="!(parentCertificate.revoked || parentCertificate.expired)"
              >
                New Certificate
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
          <template v-slot:[`item.name`]="{ item }">
            <v-btn
              class="ma-1"
              color="blue darken-2"
              plain
              v-html="item.name"
              @click="selectCertificate(item)"
            >
            </v-btn>
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
              <v-btn class=""
                text
                :disabled="!item.crl_distribution_url"
                @click="downloadCRL(item.id)">
                CRL
                <v-icon class="" color="grey darken-2">
                mdi-download
              </v-icon>
              </v-btn>
              <v-btn class=""
                text
                :disabled="!item.crl_distribution_url"
                @click="renewCRL(item.id)">
                CRL
                <v-icon class="mr-2" color="green darken-2">
                mdi-sync
                </v-icon>
              </v-btn>
            </span>
          </template>
        </v-data-table>
      </v-card>
    </v-col>
  </v-row>

  <v-dialog v-model='dialog' width='800px'>
    <forms-IntermediateCert :parent="this.parentCertificate"
                    v-on:close-dialog="closeDialog"
                    v-on:update-dasboard="updateDashboard" ref="intermediateCertForm"/>
  </v-dialog>
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
  <v-dialog v-model="dialogRenewCrl" max-width="565px">
    <v-card>
      <v-card-title class="text-h5">Enter passphrase to renew CRL list certificate.</v-card-title>
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
            <ValidationProvider name="passphrase_in" vid="passphrase_in" rules="required"
                                v-slot="{ errors }">
            <v-text-field
              prepend-icon="lock"
              name="passphrase"
              label="Passphrase"
              id="passphrase"
              v-model="renewcrl.passphrase_in"
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
        <v-btn color="blue darken-1" text @click="closeRenewCrl">Cancel</v-btn>
        <v-btn color="blue darken-1" text
               @click="renewCRLConfirm">OK</v-btn>
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
        <div v-html="dialogErrorText"></div>
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
  name: 'DashboardIntermediate',
  data() {
    return {
      displayRevoked: false,
      parentCertificate: {
        type: '',
        name: '',
      },
      api_root: process.env.VUE_APP_ROOT_API,
      revoke: {
        passphrase_issuer: null,
      },
      renewcrl: {
        passphrase_in: null,
      },
      revoke_passphrase_visible: false,
      dialog: false,
      dialogDownloading: false,
      dialogDelete: false,
      deleteItem: null,
      dialogInfo: false,
      dialogInfoText: '',
      dialogInfoLoading: true,

      renewCrlItem: null,
      dialogRenewCrl: false,

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
        this.$refs.intermediateCertForm.resetForm();
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
      const params = { type: 'I', parent: this.parentCertificate.id };

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

      const { displayRevoked } = this;
      if (displayRevoked !== true) {
        params.revoked__exact = false;
        params.expired__exact = false;
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
      if (!Object.prototype.hasOwnProperty.call(this.parentCertificate, 'id')) {
        return;
      }
      const params = this.getRequestParams(
        this.filter,
        this.pagination,
      );
      this.loading = true;
      certificates.getAll(params)
        .then((response) => {
          this.loading = false;
          if (Array.isArray(response)) {
            this.certificates = response.map(this.getDisplayCertificate);
            this.totalCertificates = response.length;
          } else {
            const { count, results } = response;
            this.certificates = results.map(this.getDisplayCertificate);
            this.totalCertificates = count;
          }
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
        commonName: certificate.dn.commonName,
        emailAddress: certificate.dn.emailAddress,
        expiresAt: certificate.expires_at,
        revoked: certificate.revoked,
        expired: certificate.expired,
        crl_distribution_url: certificate.crl_distribution_url,
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

    downloadCRL(item) {
      this.dialogDownloading = true;
      certificates.downloadCRL(
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

    renewCRL(item) {
      this.renewCrlItem = item;
      this.dialogRenewCrl = true;
    },

    renewCRLConfirm() {
      if (this.renewCrlItem !== null) {
        certificates.renewCrl(this.renewCrlItem, this.renewcrl)
          .then(() => {
            this.updateDashboard();
            this.closeRenewCrl();
          }).catch((r) => {
            const errors = r.response.data;
            this.$refs.form.setErrors(errors);
          });
      }
    },

    closeRenewCrl() {
      this.renewcrl.passphrase_in = '';
      this.$refs.form.reset();
      this.dialogRenewCrl = false;
      this.renewClrItem = null;
    },

    closeInfo() {
      this.dialogInfo = false;
    },

    closeDialog() {
      this.dialog = false;
    },

    selectCertificate(item) {
      this.$router.push(`/dashboard/certificate/${item.id}`);
    },
    updateDashboard() {
      this.retrieveCertificates();
    },
    setupDashboard() {
      certificates.get(this.$route.params.id)
        .then((response) => {
          if (response.type !== 'R') {
            this.dialogErrorText = `${response.name} is not a root certificate`;
            this.dialogError = true;
          } else {
            this.parentCertificate = response;
            this.setRoot({
              id: this.parentCertificate.id,
              name: this.parentCertificate.name,
              active: true,
            });
            this.setIntermediate({ id: null, name: '', active: false });
            this.updateDashboard();
          }
        })
        .catch((e) => {
          this.dialogErrorText = e;
          this.dialogError = true;
        });
    },
  },
  mounted() {
    this.setupDashboard();
  },
};
</script>
