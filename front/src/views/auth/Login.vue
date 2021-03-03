<template>
    <div class="vue-template">
        <ValidationObserver ref="form" v-slot="{ handleSubmit }">
        <form @submit.prevent="handleSubmit(login)" method="post">
            <h3>Sign In</h3>
            <ValidationProvider vid="non_field_errors" v-slot="v">
               <div class="alert alert-danger" v-for="(error, index) in v.errors" :key="index">{{ error }}</div>
            </ValidationProvider>

            <div class="form-group">
                <label>Username / Email address</label>
                <ValidationProvider name="username" vid="username" rules="required" v-slot="v">
                  <input type="text"
                         name="username"
                         v-model="credentials.username"
                         class="form-control form-control-lg"
                         :class="{ 'is-invalid' : v.errors.length > 0 }"/>
                  <ul class="invalid-feedback">
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                  </ul>
                </ValidationProvider>
            </div>


            <div class="form-group">
                <label>Password</label>
                <ValidationProvider name="password" vid="password" rules="required" v-slot="v">
                  <input type="password"
                         name="password"
                         v-model="credentials.password"
                         class="form-control form-control-lg"
                         :class="{ 'is-invalid' : v.errors.length > 0 }"/>
                  <ul class="invalid-feedback">
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                  </ul>
                </ValidationProvider>
            </div>

            <button type="submit" class="btn btn-bounca-blue btn-lg btn-block">Sign In</button>

            <p class="forgot-password text-right mt-2 mb-4">
                <router-link to="/password-forgot">Forgot password?</router-link>
            </p>
        </form>
        </ValidationObserver>
    </div>
</template>



<script>
import axios from 'axios';

export default {
    data() {
        return {
            credentials: {
                username: '',
                password: ''
            },
            submitted: false,
            errors: {}
        }
    },
    methods: {
        login: function () {
            axios.post('http://127.0.0.1:8000/api/v1/auth/login/',
                this.credentials).then(response => {
                    this.$cookie.set("token", response.data.key)
                    this.$emit("authenticated", true);
                    this.$router.replace({ name: "secure" });
            }).catch(r => {
                this.$refs.form.setErrors(r.response.data)
            });
        }
    }
}
</script>

