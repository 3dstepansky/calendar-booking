import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватчик для добавления JWT токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const bookingService = {
  // Получить доступные слоты
  getAvailableSlots: async (date: string) => {
    const response = await api.post('/slots/available', { date });
    return response.data;
  },

  // Создать бронирование
  createBooking: async (bookingData: any) => {
    const response = await api.post('/bookings', bookingData);
    return response.data;
  },

  // Авторизация (инициация)
  login: () => {
    window.location.href = '/api/v1/auth/login';
  }
};

export default api;
