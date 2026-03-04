from django.db import models


class Tenant(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    clinic_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    specialty = models.CharField(max_length=100)
    language_preference = models.CharField(max_length=50, default="english")
    whatsapp_number = models.CharField(max_length=20)
    plan = models.CharField(max_length=50, default="free")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
