import client from './client';

export const patientsApi = {
  list: (page = 1, perPage = 20) =>
    client.get(`/patients?page=${page}&per_page=${perPage}`),

  get: (id: string) => client.get(`/patients/${id}`),

  create: (data: {
    name: string;
    phone: string;
    age?: number;
    gender?: string;
    language?: string;
  }) => client.post('/patients', data),

  update: (id: string, data: Record<string, unknown>) =>
    client.patch(`/patients/${id}`, data),
};
