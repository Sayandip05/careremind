class NotificationService:
    async def send_reminder(self, appointment_id: str, tenant_id: str):
        return {"status": "sent"}


notification_service = NotificationService()
