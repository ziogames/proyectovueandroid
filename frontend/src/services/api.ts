import axios from 'axios';

// Detectar la URL base automáticamente
let baseURL = import.meta.env.VITE_API_BASE_URL;

if (!baseURL) {
    // En desarrollo local (localhost)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        baseURL = 'http://192.168.1.36:8000/api/';
    } else {
        // En red local (acceso por IP desde celular u otro dispositivo)
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        // Siempre usa puerto 8000 para el backend en desarrollo
        baseURL = `${protocol}//${hostname}:8000/api/`;
    }
}

const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
