import session from './session';


// TODO use config param for URI

export default {
  login(data) {
    return session.post('http://localhost:8000/api/v1/auth/login/', data);
  },
  logout() {
    return session.post('http://localhost:8000/api/v1/auth/logout/', {});
  },
  createAccount(data) {
    return session.post('http://localhost:8000/api/v1/auth/registration/', data);
  },
  changeAccountPassword(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/change/', data);
  },
  sendAccountPasswordResetEmail(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/reset/', data);
  },
  resetAccountPassword(data) {
    return session.post('http://localhost:8000/api/v1/auth/password/reset/confirm/', data);
  },
  getAccountDetails() {
    return session.get('http://localhost:8000/api/v1/auth/user/');
  },
  updateAccountDetails(data) {
    return session.patch('http://localhost:8000/api/v1/auth/user/', data);
  },
  verifyAccountEmail(data) {
    return session.post('http://localhost:8000/api/v1/registration/verify-email/', data);
  },
};
