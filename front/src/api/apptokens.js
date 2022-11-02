import axios from 'axios';
import store from '../store';

export default {
  getAll(params) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/tokens`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { params, headers: headers }).then((response) => response.data);
  },
  get(id) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/tokens/${id}`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { headers: headers }).then((response) => response.data);
  },
  delete(id, data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/tokens/${id}`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.delete(url, { data: data, headers: headers }).then((response) => response.data);
  },
  create(data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/auth/tokens/`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.post(url, data, { headers: headers });
  },
};
