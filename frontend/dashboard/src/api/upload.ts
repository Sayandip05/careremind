export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/upload/excel', formData);
};
