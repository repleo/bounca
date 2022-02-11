const packageJson = JSON.parse(JSON.stringify(require('../../package.json')));

const initialState = {
  packageVersion: packageJson.version,
};

const getters = {
  appVersion: (state) => state.packageVersion,
};

const actions = { };

const mutations = { };

export default {
  namespaced: true,
  state: initialState,
  getters,
  actions,
  mutations,
};
