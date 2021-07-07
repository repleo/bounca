import session from './session';


export default {
  create(data) {
    return session.post('http://localhost:8000/api/v1/certificates/', data);
  },
  detail(id) {
    return session.get(`http://localhost:8000/api/v1/certificates/${id}`);
  },
  list() {
    return session.get('http://localhost:8000/api/v1/certificates/');
  },
};
