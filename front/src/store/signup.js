import auth from '../api/auth';

import {
  ACTIVATION_BEGIN,
  ACTIVATION_CLEAR,
  ACTIVATION_FAILURE,
  ACTIVATION_SUCCESS,
  REGISTRATION_BEGIN,
  REGISTRATION_CLEAR,
  REGISTRATION_FAILURE,
  REGISTRATION_SUCCESS,
} from './types';

export default {
  namespaced: true,
  state: {
    activationCompleted: false,
    activationError: false,
    activationLoading: false,
    registrationCompleted: false,
    registrationError: false,
    registrationLoading: false,
  },
  actions: {
    createAccount({ commit }, { username, password1, password2, email }) {
      commit(REGISTRATION_BEGIN);
      return auth.createAccount(username, password1, password2, email)
        .then(() => commit(REGISTRATION_SUCCESS))
        .catch(() => commit(REGISTRATION_FAILURE));
    },
    activateAccount({ commit }, { key }) {
      commit(ACTIVATION_BEGIN);
      return auth.verifyAccountEmail(key)
        .then(() => commit(ACTIVATION_SUCCESS))
        .catch(() => commit(ACTIVATION_FAILURE));
    },
    clearRegistrationStatus({ commit }) {
      commit(REGISTRATION_CLEAR);
    },
    clearActivationStatus({ commit }) {
      commit(ACTIVATION_CLEAR);
    },
  },
  mutations: {
    [ACTIVATION_BEGIN](state) {
      state.activationLoading = true;
    },
    [ACTIVATION_CLEAR](state) {
      state.activationCompleted = false;
      state.activationError = false;
      state.activationLoading = false;
    },
    [ACTIVATION_FAILURE](state) {
      state.activationError = true;
      state.activationLoading = false;
    },
    [ACTIVATION_SUCCESS](state) {
      state.activationCompleted = true;
      state.activationError = false;
      state.activationLoading = false;
    },
    [REGISTRATION_BEGIN](state) {
      state.registrationLoading = true;
    },
    [REGISTRATION_CLEAR](state) {
      state.registrationCompleted = false;
      state.registrationError = false;
      state.registrationLoading = false;
    },
    [REGISTRATION_FAILURE](state) {
      state.registrationError = true;
      state.registrationLoading = false;
    },
    [REGISTRATION_SUCCESS](state) {
      state.registrationCompleted = true;
      state.registrationError = false;
      state.registrationLoading = false;
    },
  },
};
