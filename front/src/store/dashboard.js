const initialState = {
  navigation: {
    root: {
      id: '',
      name: '',
      active: false,
    },
    intermediate: {
      id: '',
      name: '',
      active: false,
    },
  },
};

const getters = { };

const actions = { };

const mutations = {
  setRoot(state, certInfo) {
    state.navigation.root = certInfo;
  },
  setIntermediate(state, certInfo) {
    state.navigation.intermediate = certInfo;
  },
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
