import axios from 'axios';
import store from '../store';

export default {
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
