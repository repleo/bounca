<!-- https://github.com/jakemcdermott/vue-django-rest-auth/blob/master/client/src/views/PasswordReset.vue -->

<!--<template>-->
<!--  <div id="activate-account-view">-->
<!--    <h1>Verify Email</h1>-->
<!--    <template v-if="activationLoading">loading...</template>-->
<!--    <template v-else-if="activationError">An error occured.</template>-->
<!--    <template v-else-if="activationCompleted">-->
<!--      Account activation successful.-->
<!--      <router-link v-if="!isAuthenticated" to="/login">-->
<!--        Click here to sign in.-->
<!--      </router-link>-->
<!--    </template>-->
<!--  </div>-->
<!--</template>-->

<!--<script>-->
<!--import {-->
<!--  mapActions,-->
<!--  mapGetters,-->
<!--  mapState,-->
<!--} from 'vuex';-->
<!--export default {-->
<!--  computed: {-->
<!--    ...mapGetters('auth', ['isAuthenticated']),-->
<!--    ...mapState('signup', [-->
<!--      'activationCompleted',-->
<!--      'activationError',-->
<!--      'activationLoading',-->
<!--    ]),-->
<!--  },-->
<!--  methods: mapActions('signup', [-->
<!--    'activateAccount',-->
<!--    'clearActivationStatus',-->
<!--  ]),-->
<!--  created() {-->
<!--    this.activateAccount(this.$route.params);-->
<!--  },-->
<!--  beforeRouteLeave(to, from, next) {-->
<!--    this.clearActivationStatus();-->
<!--    next();-->
<!--  },-->
<!--};-->
<!--</script>-->
<template>
    <div class="vue-template">
        <form>
            <h3>Forgot Password</h3>

            <div class="form-group">
                <label>Email address</label>
                <input type="email" class="form-control form-control-lg" />
            </div>

            <button type="submit" class="btn btn-dark btn-lg btn-block">Reset password</button>

        </form>
    </div>
</template>

<script>
    export default {
        data() {
            return {}
        }
    }
</script>
