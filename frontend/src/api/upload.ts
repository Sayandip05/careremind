import client from './client';

export const uploadApi = {
  uploadExcel: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/upload/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  uploadPhoto: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/upload/photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60_000, // VLM can take up to 30–40s for complex images
    });
  },

  /**
   * Step 2 of the human-in-the-loop photo flow.
   * Doctor has reviewed extracted rows — send confirmed rows to save.
   */
  confirmPhoto: (body: {
    upload_id: string;
    confirmed_rows: {
      name: string;
      phone: string;
      visit_date: string | null;
      next_visit_date: string | null;
    }[];
  }) => client.post('/upload/photo/confirm', body),
};

