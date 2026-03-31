import { create } from 'zustand';

export const useTenantStore = create((set) => ({
  tenantId: null,
  setTenantId: (id: string | null) => set({ tenantId: id }),
}));
