import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:5555/',
    withCredentials: true
})

export const register = payload => api.post(`/register`, payload)
export const update = payload => api.post(`/update`, payload)
export const validate = payload => api.post(`/validate`, payload)
export const renew = payload => api.post(`/renew`, payload)

const apis = {
    register,
    update,
    validate,
    renew
}

export default apis