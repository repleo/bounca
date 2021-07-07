<template>
  <v-container fluid>
    <v-row
      align='center'
      justify='center'
    >
      <v-col cols='10'>
        <v-card>
          <v-data-table :headers='headers' :items='items'>
            <template slot='headerCell' slot-scope='{ header }'>
              <span class='font-weight-light text-warning text--darken-3' v-text='header.text'/>
            </template>
            <template slot='items' slot-scope='{ index, item }'>
              <td>{{ index + 1 }}</td>
              <td>{{ item.name }}</td>
              <td class='text-xs-right'>{{ item.salary }}</td>
              <td class='text-xs-right'>{{ item.country }}</td>
              <td class='text-xs-right'>{{ item.city }}</td>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
    <v-btn fab dark large color='pink' fixed right bottom @click='dialog = !dialog'>
      <v-icon dark>add</v-icon>
    </v-btn>
    <v-dialog v-model='dialog' width='800px'>
      <forms-RootCert v-on:close-dialog="closeDialog"/>
<!--      <v-card class="elevation-10">-->
<!--        <v-toolbar dark flat color="primary">-->
<!--          <v-toolbar-title>Create Root Certificate</v-toolbar-title>-->
<!--        </v-toolbar>-->
<!--        <forms-RootCert/>-->
<!--        <v-card-actions class="mr-2 pb-4" >-->
<!--          <v-btn-->
<!--            color="darkgrey"-->
<!--            plain-->
<!--            text-->
<!--            :to="{ name: 'auth_login'}"-->
<!--          >-->
<!--            sign in?-->
<!--          </v-btn>-->
<!--          <v-spacer></v-spacer>-->
<!--          <v-btn-->
<!--            dark-->
<!--            color="secondary"-->
<!--            class="px-4"-->
<!--            @click="register"-->
<!--          >-->
<!--            Register-->
<!--          </v-btn>-->
<!--        </v-card-actions>-->
<!--      </v-card>-->

<!--      <v-card class="elevation-10">-->
<!--        <v-toolbar dark flat color="primary">-->
<!--          <v-toolbar-title>Create Root Certificate</v-toolbar-title>-->
<!--        </v-toolbar>-->
<!--        <forms-RootCert/>-->
<!--        <v-card-actions class="mr-2 pb-4" >-->
<!--          <v-btn-->
<!--            color="darkgrey"-->
<!--            plain-->
<!--            text-->
<!--            :to="{ name: 'auth_login'}"-->
<!--          >-->
<!--            sign in?-->
<!--          </v-btn>-->
<!--          <v-spacer></v-spacer>-->
<!--          <v-btn-->
<!--            dark-->
<!--            color="secondary"-->
<!--            class="px-4"-->
<!--            @click="register"-->
<!--          >-->
<!--            Register-->
<!--          </v-btn>-->
<!--        </v-card-actions>-->
<!--      </v-card>-->
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      dialog: false,
      headers: [
        {
          sortable: true,
          text: 'Name',
          value: 'name',
        },
        {
          sortable: false,
          text: 'Common name',
          value: 'commonname',
          align: 'right',
        },
        {
          sortable: false,
          text: 'Country',
          value: 'country',
          align: 'right',
        },
        {
          sortable: false,
          text: 'City',
          value: 'city',
          align: 'right',
        },
      ],
      items: [
        {
          name: 'Dakota Rice',
          country: 'Niger',
          city: 'Oud-Tunrhout',
          salary: '$35,738',
        },
        {
          name: 'Minerva Hooper',
          country: 'Curaçao',
          city: 'Sinaai-Waas',
          salary: '$23,738',
        }, {
          name: 'Sage Rodriguez',
          country: 'Netherlands',
          city: 'Overland Park',
          salary: '$56,142',
        }, {
          name: 'Philip Chanley',
          country: 'Korea, South',
          city: 'Gloucester',
          salary: '$38,735',
        }, {
          name: 'Doris Greene',
          country: 'Malawi',
          city: 'Feldkirchen in Kārnten',
          salary: '$63,542',
        },
      ],
      formfields:
        {
          id: {
            type: 'integer', required: false, read_only: true, label: 'ID',
          },
          owner: {
            type: 'field', required: true, read_only: false, label: 'Owner',
          },
          name: {
            type: 'string',
            required: false,
            read_only: false,
            label: 'Name',
            help_text: 'Name of your key, if not set will be equal to your CommonName.',
            max_length: 128,
          },
          parent: {
            type: 'field',
            required: false,
            read_only: false,
            label: 'Parent',
            help_text: 'The signing authority (None for root certificate)',
          },
          type: {
            type: 'choice',
            required: true,
            read_only: false,
            label: 'Type',
            choices: [{
              value: 'R', display_name: 'Root CA Certificate' }, {
              value: 'I', display_name: 'Intermediate CA Certificate',
            }, { value: 'S', display_name: 'Server Certificate' }, {
              value: 'C',
              display_name: 'Client Certificate',
            }, { value: 'O', display_name: 'OCSP Signing Certificate' }],
          },
          dn: {
            type: 'nested object',
            required: true,
            read_only: false,
            label: 'Dn',
            children: {
              commonName: {
                type: 'string',
                required: true,
                read_only: false,
                label: 'Common Name',
                help_text: 'The fully qualified domain name (FQDN) of your server. This must match exactly what you type in your web browser or you will receive a name mismatch error.',
                max_length: 64,
              },
              countryName: {
                type: 'choice',
                required: false,
                read_only: false,
                label: 'Country Name',
                help_text: 'The two-character country name in ISO 3166 format.',
                choices: [
                  { value: 'AF', display_name: 'Afghanistan' },
                  { value: 'AX', display_name: 'Åland Islands' },
                  { value: 'AL', display_name: 'Albania' },
                  { value: 'DZ', display_name: 'Algeria' },
                  { value: 'AS', display_name: 'American Samoa' },
                  { value: 'AD', display_name: 'Andorra' },
                  { value: 'AO', display_name: 'Angola' },
                  { value: 'AI', display_name: 'Anguilla' },
                  { value: 'AQ', display_name: 'Antarctica' },
                  { value: 'AG', display_name: 'Antigua and Barbuda' },
                  { value: 'AR', display_name: 'Argentina' },
                  { value: 'AM', display_name: 'Armenia' },
                  { value: 'AW', display_name: 'Aruba' },
                  { value: 'AU', display_name: 'Australia' },
                  { value: 'AT', display_name: 'Austria' },
                ],
              },
              stateOrProvinceName: {
                type: 'string',
                required: false,
                read_only: false,
                label: 'State or Province Name',
                help_text: 'The state/region where your organization is located. This shouldn\'t be abbreviated. (1–128 characters)',
                max_length: 128,
              },
              localityName: {
                type: 'string',
                required: false,
                read_only: false,
                label: 'Locality Name',
                help_text: 'The city where your organization is located. (1–128 characters)',
                max_length: 128,
              },
              organizationName: {
                type: 'string',
                required: false,
                read_only: false,
                label: 'Organization Name',
                help_text: 'The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.',
                max_length: 64,
              },
              organizationalUnitName: {
                type: 'string',
                required: false,
                read_only: false,
                label: 'Organization Unit Name',
                help_text: 'The division of your organization handling the certificate.',
                max_length: 64,
              },
              emailAddress: {
                type: 'email',
                required: false,
                read_only: false,
                label: 'Email Address',
                help_text: 'The email address to contact your organization. Also used by BounCA for authentication.',
                max_length: 64,
              },
              subjectAltNames: {
                type: 'list',
                required: false,
                read_only: false,
                label: 'SubjectAltNames',
                help_text: 'subjectAltName list, i.e. dns names for server certs and email adresses for client certs. (separate by comma)',
                child: {
                  type: 'string',
                  required: true,
                  read_only: false,
                  label: 'SubjectAltNames',
                  max_length: 64,
                },
              },
            },
          },
          created_at: { type: 'date', required: false, read_only: true, label: 'Created at' },
          expires_at: {
            type: 'date',
            required: true,
            read_only: false,
            label: 'Expires at',
            help_text: 'Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year. Allowed date format: yyyy-mm-dd.',
          },
          revoked_at: { type: 'date', required: false, read_only: true, label: 'Revoked at' },
          days_valid: { type: 'field', required: false, read_only: true, label: 'Days valid' },
          expired: { type: 'field', required: false, read_only: true, label: 'Expired' },
          revoked: { type: 'field', required: false, read_only: true, label: 'Revoked' },
          crl_distribution_url: {
            type: 'url',
            required: false,
            read_only: false,
            label: 'CRL distribution url',
            help_text: 'Base URL for certificate revocation list (CRL)',
            max_length: 200,
          },
          ocsp_distribution_host: {
            type: 'url',
            required: false,
            read_only: false,
            label: 'OCSP distribution host',
            help_text: 'Host URL for Online Certificate Status Protocol (OCSP)',
            max_length: 200,
          },
          passphrase_issuer: {
            type: 'string',
            required: false,
            read_only: false,
            label: 'Passphrase issuer',
            max_length: 200,
          },
          passphrase_out: {
            type: 'string',
            required: false,
            read_only: false,
            label: 'Passphrase out',
            max_length: 200,
          },
          passphrase_out_confirmation: {
            type: 'string',
            required: false,
            read_only: false,
            label: 'Passphrase out confirmation',
            max_length: 200,
          },
        },
    };
  },
  methods: {
    complete(index) {
      this.list[index] = !this.list[index];
    },
    closeDialog() {
      console.log('close dialog 2');
      this.dialog = false;
    },
  },
};
</script>
