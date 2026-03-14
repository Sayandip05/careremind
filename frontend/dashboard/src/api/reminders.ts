import client from './client';

export const remindersApi = {
  list: (page = 1, perPage = 20, status?: string) => {
    let url = `/reminders?page=${page}&per_page=${perPage}`;
    if (status) url += `&status=${status}`;
    return client.get(url);
  },
};
