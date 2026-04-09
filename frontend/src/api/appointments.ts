import client from './client';

export const appointmentsApi = {
  // List all appointments
  list: (page = 1, perPage = 20, patientId?: string) => {
    const params: Record<string, any> = { page, per_page: perPage };
    if (patientId) params.patient_id = patientId;
    return client.get('/appointments', { params });
  },

  // Create a new appointment
  create: (data: {
    patient_id: string;
    visit_date: string;
    next_visit_date?: string;
    appointment_type?: string;
    specialty_override?: string;
    notes?: string;
    source?: string;
  }) => client.post('/appointments', data),

  // Get a single appointment
  get: (id: string) => client.get(`/appointments/${id}`),
};
