from django.db import models


class Staff(models.Model):
    ROLE_CHOICES = [
        ("doctor", "Doctor"),
        ("receptionist", "Receptionist"),
        ("admin", "Admin"),
    ]

    id = models.CharField(max_length=100, primary_key=True)
    tenant_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
