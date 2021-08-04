import session from './session';
import axios from 'axios';
import store from "@/api/store";
const API_URL = 'http://localhost:8000';


export default {
  // done
  create(data){
    const url = `${API_URL}/api/v1/certificates/`;
    const headers = {Authorization: `Token ${store.getters.accessToken}`};
    return axios.post(url,data,{headers: headers});
  }
};


// export class APIService{
//
//     getProducts() {
//         const url = `${API_URL}/api/v1/certificates/`;
//         return axios.get(url, { headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` }}).then(response => response.data);
//     }
//     getProductsByURL(link){
//         const url = `${API_URL}${link}`;
//         return axios.get(url, { headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` }}).then(response => response.data);
//
//     }
//     getProduct(pk) {
//         const url = `${API_URL}/api/v1/certificates/${pk}`;
//         return axios.get(url, { headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` }}).then(response => response.data);
//     }
//     deleteProduct(product){
//         const url = `${API_URL}/api/v1/certificates/${product.pk}`;
//         return axios.delete(url, { headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` }});
//
//     }
//     createProduct(product){
//         const url = `${API_URL}/api/v1/certificates/`;
//         const headers = {Authorization: `Bearer ${AuthService.getAuthToken()}`};
//         return axios.post(url,product,{headers: headers});
//     }
//     updateProduct(product){
//         const url = `${API_URL}/api/v1/certificates/${product.pk}`;
//         const headers = {Authorization: `Bearer ${AuthService.getAuthToken()}`};
//         return axios.put(url,product,{headers: headers});
//     }
// }
