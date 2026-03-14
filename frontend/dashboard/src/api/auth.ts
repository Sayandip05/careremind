import client from './client';

export const authApi = {
  login: (email: string, password: string) =>
    client.post('/auth/login', { email, password }),

  register: (data: {
    doctor_name: string;
    clinic_name: string;
    email: string;
    password: string;
    phone?: string;
    specialty?: string;
    whatsapp_number?: string;
  }) => client.post('/auth/register', data),

  getProfile: () => client.get('/auth/me'),
};
