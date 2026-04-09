import client from './client';

export const staffApi = {
  // List all staff members
  list: (page = 1, perPage = 20) =>
    client.get('/staff', {
      params: { page, per_page: perPage },
    }),

  // Create a new staff member
  create: (data: {
    name: string;
    role: string;
    phone?: string;
    email?: string;
  }) => client.post('/staff', data),

  // Get a single staff member
  get: (id: string) => client.get(`/staff/${id}`),

  // Update a staff member
  update: (
    id: string,
    data: {
      name?: string;
      role?: string;
      phone?: string;
      email?: string;
      is_active?: boolean;
    }
  ) => client.patch(`/staff/${id}`, data),

  // Delete a staff member
  delete: (id: string) => client.delete(`/staff/${id}`),
};
