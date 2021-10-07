import axios from 'axios';
import store from '@/store';
import session from './session';


// TODO use config param for URI
const API_URL = 'http://localhost:8000';

export default {
  //
  login(data) {
    return session.post(`${API_URL}/api/v1/auth/login/`, data);
  },
  logout() {
    return session.post(`${API_URL}/api/v1/auth/logout/`, {});
  },
  //
  createAccount(data) {
    return session.post(`${API_URL}/api/v1/auth/registration/`, data);
  },
  //
  sendAccountPasswordResetEmail(data) {
    return session.post(`${API_URL}/api/v1/auth/password/reset/`, data);
  },
  //
  resetAccountPassword(data) {
    return session.post(`${API_URL}/api/v1/auth/password/reset/confirm/`, data);
  },
  //
  verifyAccountEmail(data) {
    return session.post(`${API_URL}/api/v1/auth/registration/verify-email/`, data);
  },
  // for profile menu
  changeAccountPassword(data) {
    const url = `${API_URL}/api/v1/auth/password/change/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.post(url, data, { headers: headers });
  },
  getAccountDetails() {
    const url = `${API_URL}/api/v1/auth/user/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { headers: headers });
  },
  updateAccountDetails(data) {
    const url = `${API_URL}/api/v1/auth/user/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.patch(url, data, { headers: headers });
  },

};
