import auth from '../api/auth';

import {
  PASSWORD_RESET_BEGIN,
  PASSWORD_RESET_CLEAR,
  PASSWORD_RESET_FAILURE,
  PASSWORD_RESET_SUCCESS,
  PASSWORD_EMAIL_BEGIN,
  PASSWORD_EMAIL_CLEAR,
  PASSWORD_EMAIL_FAILURE,
  PASSWORD_EMAIL_SUCCESS,
} from './types';

export default {
  namespaced: true,
  state: {
    emailCompleted: false,
    emailError: false,
    emailLoading: false,
    resetCompleted: false,
    resetError: false,
    resetLoading: false,
  },
  actions: {
    resetPassword({ commit }, { uid, token, password1, password2 }) {
      commit(PASSWORD_RESET_BEGIN);
      return auth.resetAccountPassword(uid, token, password1, password2)
        .then(() => commit(PASSWORD_RESET_SUCCESS))
        .catch(() => commit(PASSWORD_RESET_FAILURE));
    },
    sendPasswordResetEmail({ commit }, { email }) {
      commit(PASSWORD_EMAIL_BEGIN);
      return auth.sendAccountPasswordResetEmail(email)
        .then(() => commit(PASSWORD_EMAIL_SUCCESS))
        .catch(() => commit(PASSWORD_EMAIL_FAILURE));
    },
    clearResetStatus({ commit }) {
      commit(PASSWORD_RESET_CLEAR);
    },
    clearEmailStatus({ commit }) {
      commit(PASSWORD_EMAIL_CLEAR);
    },
  },
  mutations: {
    [PASSWORD_RESET_BEGIN](state) {
      state.resetLoading = true;
    },
    [PASSWORD_RESET_CLEAR](state) {
      state.resetCompleted = false;
      state.resetError = false;
      state.resetLoading = false;
    },
    [PASSWORD_RESET_FAILURE](state) {
      state.resetError = true;
      state.resetLoading = false;
    },
    [PASSWORD_RESET_SUCCESS](state) {
      state.resetCompleted = true;
      state.resetError = false;
      state.resetLoading = false;
    },
    [PASSWORD_EMAIL_BEGIN](state) {
      state.emailLoading = true;
    },
    [PASSWORD_EMAIL_CLEAR](state) {
      state.emailCompleted = false;
      state.emailError = false;
      state.emailLoading = false;
    },
    [PASSWORD_EMAIL_FAILURE](state) {
      state.emailError = true;
      state.emailLoading = false;
    },
    [PASSWORD_EMAIL_SUCCESS](state) {
      state.emailCompleted = true;
      state.emailError = false;
      state.emailLoading = false;
    },
  },
};
