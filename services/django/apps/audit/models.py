from django.db import models


class AuditLog(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    tenant_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=50)
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
