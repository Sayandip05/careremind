import client from './client';

export const getPatients = () => client.get('/patients');
export const createPatient = (data) => client.post('/patients', data);
