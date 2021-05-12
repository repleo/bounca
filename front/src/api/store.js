import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';
import auth from '@/api/auth';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    key: localStorage.getItem('key') || '',
  },
  mutations: {
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
  },
  actions: {
    login({ commit }, credentials) {
      return new Promise((resolve, reject) => {
        commit('auth_request');
        auth.login(credentials).then((resp) => {
          const key = resp.data.key;
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
    register({ commit }, user) {
      return new Promise((resolve, reject) => {
        commit('auth_request');
        auth.createAccount(user).then((resp) => {
          const key = resp.data.key;
          localStorage.setItem('key', key);
          // Add the following line:
          commit('auth_success', key);
          axios.defaults.headers.common.Authorization = key;
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
          console.log(err);
          reject(err);
        });
      });
    },
  },
  getters: {
    isLoggedIn: state => !!state.key,
  },
});
