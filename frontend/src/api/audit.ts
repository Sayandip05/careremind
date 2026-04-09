import client from './client';

export const auditApi = {
  // List audit logs with optional filters
  list: (
    page = 1,
    perPage = 20,
    filters?: {
      action?: string;
      resource?: string;
      resource_id?: string;
      user_id?: string;
    }
  ) => {
    const params: Record<string, any> = { page, per_page: perPage };
    if (filters) {
      if (filters.action) params.action = filters.action;
      if (filters.resource) params.resource = filters.resource;
      if (filters.resource_id) params.resource_id = filters.resource_id;
      if (filters.user_id) params.user_id = filters.user_id;
    }
    return client.get('/audit', { params });
  },
};
