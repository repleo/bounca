import session from './session';


// TODO use config param for URI

export default {
  // done
  login(data) {
    return session.post('http://localhost:8000/api/v1/auth/login/', data);
  },
  logout() {
    return session.post('http://localhost:8000/api/v1/auth/logout/', {});
  },
  // done
  createAccount(data) {
    return session.post('http://localhost:8000/api/v1/auth/registration/', data);
  },
  // done
  sendAccountPasswordResetEmail(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/reset/', data);
  },
  // done
  resetAccountPassword(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/reset/confirm/', data);
  },
  // done
  verifyAccountEmail(data) {
    return session.post('http://localhost:8000/api/v1/auth/registration/verify-email/', data);
  },
  // for profile menu
  changeAccountPassword(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/change/', data);
  },
  getAccountDetails() {
    return session.get('http://localhost:8000/api/v1/auth/user/');
  },
  updateAccountDetails(data) {
    return session.patch('http://localhost:8000/api/v1/auth/user/', data);
  },

};
