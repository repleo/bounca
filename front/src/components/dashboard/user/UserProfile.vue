<template>
  <v-container
    fill-height
    fluid
    grid-list-xl>
    <v-layout
      justify-center
      wrap
    >
      <v-flex xs12 md8>
        <h3>User Profile</h3>
      </v-flex>
      <v-flex
        xs12
        md8
      >
      <forms-UserChangeProfile ref="changeProfile"/>
      </v-flex>

      <v-flex
        xs12
        md8
      >
      <forms-UserChangePassword ref="changePassword" @success="showDialog($event)"/>
      </v-flex>

      <v-flex
        xs12
        md8
      >
      </v-flex>
      <v-flex
        xs12
        md8
      >
        <v-data-table
          :headers="headers"
          :items="apptokens"
          :options.sync="pagination"
          :server-items-length="totalApptokens"
          :loading="loading"
          :page.sync="page"
          class="elevation-1"
          :footer-props="{'items-per-page options': items_per_page_selector}"
        >
          <template v-slot:top>
            <v-toolbar
              flat
            >
              <v-toolbar-title> App Tokens</v-toolbar-title>
              <v-spacer></v-spacer>
                <v-btn
                color="primary"
                dark
                class="mb-2"
                @click='addTokenDialog = !addTokenDialog'
              >
                Add Token
              </v-btn>
            </v-toolbar>

          </template>
          <template v-slot:[`item.actions`]="{ item }">
              <v-icon class="mr-2" color="red darken-2" @click="deleteAppToken(item.id)">
                mdi-delete
              </v-icon>
          </template>
        </v-data-table>

      </v-flex>

      <v-flex
        xs12
        md8
      >
      <forms-UserDeleteAccount ref="deleteAccount" @success="showDialog($event)"/>
      </v-flex>
    </v-layout>

    <v-dialog v-model='addTokenDialog' width='800px'>
    <forms-UserAddToken v-on:close-dialog="closeAddTokenDialog"
                    v-on:update-dashboard="updateAddTokenDashboard" ref="addToken"/>
    </v-dialog>

    <v-dialog v-model="dialogDelete" max-width="565px">
      <v-card>
      <v-card-title class="text-h5">Are you sure you want to
        revoke app token?</v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="closeDialogDelete">Cancel</v-btn>
        <v-btn color="blue darken-1" text
               @click="deleteAppTokenConfirm">OK</v-btn>
      </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      dialog: false,
      dialogText: '',
    };
  },
  methods: {
    showDialog(dialogText) {
      this.dialog = true;
      this.dialogText = dialogText;
    },
  },
};
</script>

<script>
// import {
//   mapMutations,
// } from 'vuex';

import apptokens from "@/api/apptokens";

export default {
  name: 'DashboardAppTokens',
  data() {
    return {
      loading: true,
      addTokenDialog: false,
      dialogDelete: false,
      items_per_page_selector: [10, 25, 50],
      pagination: {},
      apptokens: [],
      filter: '',
      headers: [
        {
          text: 'name', align: 'start', sortable: true, value: 'name',
        },
        {
          text: 'token', value: 'token', sortable: false,
        },
        {
          text: 'Actions', value: 'actions', sortable: false,
        },
      ],
      page: 1,
      totalApptokens: 0,
    };
  },
  watch: {
    dialogDelete(val) {
      if (!val) {
        this.closeRevoke();
      }
    },
    addTokenDialog(val) {
      if (!val) {
        this.$refs.AddTokenForm.resetForm();
      }
    },
    pagination: {
      handler() {
        this.updateAddTokenDashboard();
      },
      deep: true,
    },
  },
  methods: {
    getRequestParams(filter, pagination) {
      const params = { };
      if ('sortBy' in pagination && pagination.sortBy.length === 1
        && 'sortDesc' in pagination && pagination.sortDesc.length === 1) {
        const [sortBy] = pagination.sortBy;
        params.ordering = sortBy;
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

      if ('itemsPerPage' in pagination && pagination.itemsPerPage > 0) {
        const { itemsPerPage } = pagination;
        params.page_size = itemsPerPage;
      }

      return params;
    },

    retrieveAppTokens() {
      const params = this.getRequestParams(
        this.filter,
        this.pagination,
      );
      this.loading = true;
      apptokens.getAll(params)
        .then((response) => {
          this.loading = false;
          if (Array.isArray(response)) {
            this.apptokens = response.map(this.getDisplayAppToken);
            this.totalApptokens = response.length;
          } else {
            const { count, results } = response;
            this.apptokens = results.map(this.getDisplayAppToken);
            this.totalApptokens = count;
          }
        })
        .catch((e) => {
          this.dialogErrorText = e;
          this.dialogError = true;
        });
    },

    getDisplayAppToken(apptoken) {
      return {
        id: apptoken.id,
        name: apptoken.name,
        token: apptoken.token,
      };
    },

    deleteAppToken(item) {
      this.deleteItem = item;
      this.dialogDelete = true;
    },

    deleteAppTokenConfirm() {
      if (this.deleteItem !== null) {
        apptokens.delete(this.deleteItem, this.revoke)
          .then(() => {
            this.updateAddTokenDashboard();
            this.closeDialogDelete();
          }).catch((r) => {
            this.closeDialogDelete();
          });
      }
    },

    closeDialogDelete() {
      this.dialogDelete = false;
      this.deleteItem = null;
    },

    closeInfo() {
      this.dialogInfo = false;
    },

    closeDialog() {
      this.dialog = false;
    },

    closeAddTokenDialog() {
      this.addTokenDialog = false;
    },

    updateAddTokenDashboard() {
      this.retrieveAppTokens();
    },
    setupDashboard() {
      apptokens.getAll()
        .then((response) => {
          this.loading = false;
          if (Array.isArray(response)) {
            this.apptokens = response.map(this.getDisplayAppToken);
            this.totalApptokens = response.length;
          } else {
            const { count, results } = response;
            this.apptokens = results.map(this.getDisplayAppToken);
            this.totalApptokens = count;
          }
          this.updateAddTokenDashboard();
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
