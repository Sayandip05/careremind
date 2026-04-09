import client from './client';

export const clinicsApi = {
  // List all clinic locations
  list: (page = 1, perPage = 20) =>
    client.get('/clinics', {
      params: { page, per_page: perPage },
    }),

  // Create a new clinic location
  create: (data: {
    clinic_name: string;
    address_line: string;
    city: string;
    pincode: string;
    phone?: string;
  }) => client.post('/clinics', data),

  // Get a single clinic location
  get: (id: string) => client.get(`/clinics/${id}`),

  // Update a clinic location
  update: (
    id: string,
    data: {
      clinic_name?: string;
      address_line?: string;
      city?: string;
      pincode?: string;
      phone?: string;
      is_active?: boolean;
    }
  ) => client.patch(`/clinics/${id}`, data),

  // Delete a clinic location
  delete: (id: string) => client.delete(`/clinics/${id}`),
};
