import client from './client';

export const getReminders = () => client.get('/reminders');
export const triggerReminder = (id) => client.post(`/reminders/trigger/${id}`);
