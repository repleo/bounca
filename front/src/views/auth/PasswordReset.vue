<template>
    <div class="vue-template">
        <ValidationObserver ref="form" v-slot="{ handleSubmit }">
        <form @submit.prevent="handleSubmit(pwreset)" method="post">
            <h3>Forgot Password</h3>
            <ValidationProvider vid="non_field_errors" v-slot="v">
               <div class="alert alert-danger" v-for="(error, index) in v.errors" :key="index">{{ error }}</div>
            </ValidationProvider>

            <div class="form-group">
                <label>Email address</label>
                <ValidationProvider name="email" vid="email" rules="required|email" v-slot="v">
                <input type="text"
                       name="email"
                       v-model="subscription.email"
                       class="form-control form-control-lg"
                       :class="{ 'is-invalid' : typeof errors.email !== 'undefined' || v.errors.length > 0 }"/>

                <ul class="invalid-feedback">
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                </ul>
                </ValidationProvider>
            </div>


            <button type="submit" class="btn btn-bounca-blue btn-lg btn-block">Reset password</button>

            <p class="forgot-password text-right mt-2 mb-4">
                <router-link to="/login">Sign in?</router-link>
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
                email: ''
            },
            submitted: false,
            errors: {}
        }
    },
    methods: {
        login: function () {
            axios.post('http://127.0.0.1:8000/api/v1/auth/resetpassword/',
                this.credentials).then(response => {
                    this.$cookie.set("token", response.data.key)
                    this.$emit("authenticated", true);
                    this.$router.replace({ name: "secure" });
            }).catch(r => {
                console.log(r.response.data)
                this.$refs.form.setErrors(r.response.data)
            });
        }
    }
}
</script>
