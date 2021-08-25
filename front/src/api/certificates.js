import axios from 'axios';
import store from '@/api/store';

const API_URL = 'http://localhost:8000';

export default {
  getAll(params) {
    const url = `${API_URL}/api/v1/certificates/`;
    const headers = { Authorization: `Token ${store.getters.accessToken}` };
    return axios.get(url, { params, headers: headers }).then(response => response.data);
  },
  getInfo(id) {
    const url = `${API_URL}/api/v1/certificates/${id}/info`;
    const headers = { Authorization: `Token ${store.getters.accessToken}` };
    return axios.get(url, { headers: headers }).then(response => response.data);
  },
  create(data) {
    const url = `${API_URL}/api/v1/certificates/`;
    const headers = { Authorization: `Token ${store.getters.accessToken}` };
    return axios.post(url, data, { headers: headers });
  },
};
