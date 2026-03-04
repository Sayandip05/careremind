import { create } from 'zustand';

export const useTenantStore = create((set) => ({
  tenantId: null,
  setTenantId: (id) => set({ tenantId: id }),
}));
