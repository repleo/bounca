import axios from 'axios';
import store from '../store';
import router from '../router';
import session from './session';


export default {
  //
  login(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/login/`, data);
  },
  logout() {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/logout/`, {});
  },
  //
  createAccount(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/registration/`, data);
  },
  //
  sendAccountPasswordResetEmail(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/password/reset/`, data);
  },
  //
  resetAccountPassword(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/password/reset/confirm/`, data);
  },
  //
  verifyAccountEmail(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/registration/verify-email/`, data);
  },
  // for profile menu
  changeAccountPassword(data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/password/change/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.post(url, data, { headers: headers });
  },
  getAccountDetails() {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/user/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { headers: headers });
  },
  updateAccountDetails(data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/user/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.patch(url, data, { headers: headers });
  },

};

axios.interceptors.response.use(
  response => response,
  (error) => {
    if (error.response.status === 403) {
      store.dispatch('auth/logout').then(() => router.push('/'));
    }
    return error;
  });
