import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const productAPI = {
  getProducts: (params = {}) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
  searchProducts: (query) => api.get('/products', { params: { search: query } }),
};

export const cartAPI = {
  getCart: () => api.get('/cart'),
  addToCart: (productId, quantity = 1, variant = null) => 
    api.post('/cart/add', { product_id: productId, quantity, variant }),
  removeFromCart: (itemId) => api.delete(`/cart/${itemId}`),
};

export const orderAPI = {
  createOrder: (data) => api.post('/checkout', data),
  getOrders: () => api.get('/orders'),
  getOrder: (orderNumber) => api.get(`/orders/${orderNumber}`),
  trackOrder: (trackingNumber, carrier) => 
    api.get(`/track/${trackingNumber}`, { params: { carrier } }),
};

export default api;
