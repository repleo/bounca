import session from './session';

export default {
  //
  login(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/login/`, data);
  },
  logout() {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/logout/`, {});
  },
  //
  createAccount(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/registration/`, data);
  },
  //
  sendAccountPasswordResetEmail(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/password/reset/`, data);
  },
  //
  resetAccountPassword(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/password/reset/confirm/`, data);
  },
  //
  verifyAccountEmail(data) {
    return session.post(`${process.env.VUE_APP_ROOT_API}/api/v1/auth/registration/verify-email/`, data);
  },
};
