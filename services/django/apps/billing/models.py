from django.db import models


class Payment(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    tenant_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()
    plan = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
