# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    
    # "Digital Token" logic
    is_redeemed = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)

    def __str__(self):
        return f"Coupon {str(self.id)[:8]} - {self.user.display_id}"
