import axios from 'axios';
import store from '../store';

export default {
  getAll(params) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/certificates`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { params, headers: headers }).then((response) => response.data);
  },
  get(id) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/certificates/${id}`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { headers: headers }).then((response) => response.data);
  },
  getInfo(id) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/certificates/${id}/info`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.get(url, { headers: headers }).then((response) => response.data);
  },
  download(path, callback, callbackError) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/${path}`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    axios.get(url, { headers: headers, responseType: 'blob' }).then((response) => {
      const fileURL = window.URL.createObjectURL(new Blob([response.data]));
      const suggestedFileName = response.headers['content-disposition'];
      const effectiveFileName = (suggestedFileName === undefined ? 'download' : suggestedFileName.split(';')
        .find((n) => n.includes('filename='))
        .replace('filename=', '')
        .trim());
      const fileLink = document.createElement('a');
      fileLink.href = fileURL;
      fileLink.setAttribute('download', effectiveFileName);
      document.body.appendChild(fileLink);
      fileLink.click();
      callback();
    }).catch((e) => {
      callbackError(e);
    });
  },
  downloadCertificate(item, callback, callbackError) {
    this.download(
      `certificates/${item}/download`,
      callback,
      callbackError,
    );
  },
  downloadCRL(item, callback, callbackError) {
    this.download(
      `certificates/${item}/crl`,
      callback,
      callbackError,
    );
  },
  revoke(id, data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/certificates/${id}`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.delete(url, { data: data, headers: headers }).then((response) => response.data);
  },
  create(data) {
    const url = `${process.env.VUE_APP_ROOT_API}/api/v1/certificates`;
    const headers = { Authorization: `Token ${store.getters['auth/accessToken']}` };
    return axios.post(url, data, { headers: headers });
  },
};
