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
    });
  },
};
