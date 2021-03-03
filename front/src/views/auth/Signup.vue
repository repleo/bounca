<template>

    <div class="vue-template">
        <p v-if="authenticated">You are already logged in! You don't need to register.</p>
        <ValidationObserver v-else ref="form" v-slot="{ handleSubmit }">
        <form @submit.prevent="handleSubmit(signup)" method="post">
            <h3>Sign Up</h3>
            <div class="alert alert-danger" v-for="error in errors.non_field_errors" :key="error">{{error}}</div>

            <div class="form-group">
                <label>Username</label>
                <ValidationProvider name="username" vid="username" rules="required" v-slot="v">
                <input type="text"
                       name="username"
                       v-model="subscription.username"
                       class="form-control form-control-lg"
                       :class="{ 'is-invalid' : v.errors.length > 0 }"/>

                <ul class="invalid-feedback">
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                </ul>
                </ValidationProvider>
            </div>

            <div class="form-group">
                <label>Email address</label>
                <ValidationProvider name="email" vid="email" rules="required|email" v-slot="v">
                <input type="text"
                       name="email"
                       v-model="subscription.email"
                       class="form-control form-control-lg"
                       :class="{ 'is-invalid' : typeof errors.email !== 'undefined' || v.errors.length > 0 }"/>

                <ul class="invalid-feedback">
                    <li v-for="(error, index) in errors.email" :key="index">{{ error }}</li>
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                </ul>
                </ValidationProvider>
            </div>

            <div class="form-group">
                <label>Password</label>
                <ValidationProvider name="password" vid="password1" rules="required" v-slot="v">
                <input type="password"
                       name="password1"
                       v-model="subscription.password1"
                       class="form-control form-control-lg"
                       :class="{ 'is-invalid' : typeof errors.password1 !== 'undefined' || v.errors.length > 0 }"/>
                <ul class="invalid-feedback">
                    <li v-for="(error, index) in errors.password1" :key="index">{{ error }}</li>
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                </ul>
                </ValidationProvider>
            </div>

            <div class="form-group">
                <label>Password (confirm)</label>
                <ValidationProvider name="password confirmation" vid="password2" rules="required|confirmed:password1" v-slot="v">
                <input type="password"
                       name="password2"
                       v-model="subscription.password2"
                       class="form-control form-control-lg"
                       :class="{ 'is-invalid' : typeof errors.password2 !== 'undefined' || v.errors.length > 0 }"/>
                <ul class="invalid-feedback">
                    <li v-for="(error, index) in errors.password2" :key="index">{{ error }}</li>
                    <li v-for="(error, index) in v.errors" :key="index">{{ error }}</li>
                </ul>
                </ValidationProvider>

            </div>

            <button type="submit" class="btn btn-bounca-blue btn-lg btn-block">Sign Up</button>

            <p class="forgot-password text-right">
                Already registered
                <router-link :to="{name: 'login'}">sign in?</router-link>
            </p>
        </form>
        </ValidationObserver>
    </div>


</template>

<script>
import axios from "axios";
//import DjangoInput from "@/components/DjangoInput";
export default {
//    components: {DjangoInput},
    // components: {
    //      Form,
    //      Field,
    // },

    data() {
        return {
            subscription: {
                username: '',
                password1: '',
                password2: '',
                email: '',
            },
            submitted: false,
            //TODO get authentication information
            authenticated: false,
            errors: {}
        }
    },
    methods: {
        signup: function () {
            axios.post('http://127.0.0.1:8000/api/v1/auth/registration/',
                this.subscription).then(response => {
                console.log(response) //TODO fix this, remove this. redirect?
            }).catch(r => {
                this.$refs.form.setErrors(r.response.data);
                console.log(r.response.data)
            });
            //this.dialog = false
        }
        // validateBeforeSubmit() {
        //   this.$validator.validateAll().then((result) => {
        //     if (result) {
        //       // eslint-disable-next-line
        //       alert('Form Submitted!');
        //       return;
        //     }
        //
        //     alert('Correct them errors!');
        //   });
        // }
        // signupschema: Yup.object().shape({
        //     userName: Yup.string()
        //         .required('First Name is required'),
        //     email: Yup.string()
        //         .required('Email is required')
        //         .email('Email is invalid'),
        //     password: Yup.string()
        //         .min(6, 'Password must be at least 6 characters')
        //         .required('Password is required'),
        //     confirmPassword: Yup.string()
        //         .oneOf([Yup.ref('password'), null], 'Passwords must match')
        //         .required('Confirm Password is required')
        // })
    }
}
</script>
