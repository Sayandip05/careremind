import client from './client';

export const authApi = {
  login: (email: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    return client.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  register: (data: {
    doctor_name: string;
    clinic_name: string;
    email: string;
    password: string;
    phone?: string;
    specialty?: string;
    whatsapp_number?: string;
    language_preference?: string;
  }) => client.post('/auth/register', data),

  getProfile: () => client.get('/auth/me'),
};
