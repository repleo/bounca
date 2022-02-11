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
    </v-layout>
    <v-dialog v-model="dialog" width="800px">
    <v-card>
      <v-card-title class="text-h5">Info</v-card-title>
      <v-card-text>
            <v-alert
      border="right"
      colored-border
      type="info"
      elevation="2"
    >
        <div v-html="dialogText"></div>
            </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
          <v-btn
            color="blue darken-2"
            text
            @click="dialog = false"
          >
            Close
          </v-btn>
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
