import axios from 'axios';
import auth from '../api/auth';

const initialState = {
  key: localStorage.getItem('key') || '',
};

const mutations = {
  auth_request(state) {
    state.status = 'loading';
  },
  auth_success(state, key) {
    state.status = 'success';
    state.key = key;
  },
  auth_error(state) {
    state.status = 'error';
  },
  logout(state) {
    state.status = '';
    state.key = '';
  },
};

const actions = {
  login({ commit }, credentials) {
    return new Promise((resolve, reject) => {
      commit('auth_request');
      auth.login(credentials).then((resp) => {
        const { key } = resp.data;
        localStorage.setItem('key', key);
        axios.defaults.headers.common.Authorization = key;
        commit('auth_success', key);
        resolve(resp);
      }).catch((err) => {
        commit('auth_error');
        localStorage.removeItem('key');
        reject(err);
      });
    });
  },
  register({ commit }, subscription) {
    return new Promise((resolve, reject) => {
      commit('auth_request');
      auth.createAccount(subscription).then((resp) => {
        const { key } = resp.data;
        localStorage.setItem('key', key);
        axios.defaults.headers.common.Authorization = key;
        commit('auth_success', key);
        resolve(resp);
      }).catch((err) => {
        commit('auth_error');
        localStorage.removeItem('key');
        reject(err);
      });
    });
  },
  logout({ commit }) {
    return new Promise((resolve, reject) => {
      auth.logout().then((resp) => {
        commit('logout');
        localStorage.removeItem('key');
        delete axios.defaults.headers.common.Authorization;
        resolve(resp);
      }).catch((err) => {
        reject(err);
      });
    });
  },
};

const getters = {
  isLoggedIn: (state) => !!state.key,
  accessToken: (state) => state.key,
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
