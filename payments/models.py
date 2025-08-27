from django.db import models
from orders.models import Order

class PaymentStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=PaymentStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment#{self.pk} → Order#{self.order_id} · {self.status}"