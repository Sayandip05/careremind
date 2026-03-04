class TenantService:
    async def create(self, data: dict):
        return {"id": "tenant_123"}

    async def get(self, tenant_id: str):
        return {"id": tenant_id}


tenant_service = TenantService()
