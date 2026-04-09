import client from './client';

export const billingApi = {
  // Get payment history
  getHistory: (page = 1, perPage = 20) =>
    client.get('/billing/history', {
      params: { page, per_page: perPage },
    }),

  // Get subscription status
  getStatus: () => client.get('/billing/status'),
};
