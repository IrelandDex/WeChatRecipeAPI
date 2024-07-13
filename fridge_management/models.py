from django.db import models
from custom_users.models import CustomUser
from django.utils.crypto import get_random_string


class FridgeSpace(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fridge_spaces')
    name = models.CharField(max_length=100)
    share_key = models.CharField(max_length=40, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.share_key:
            self.share_key = get_random_string(30)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FridgeItem(models.Model):
    space = models.ForeignKey(FridgeSpace, on_delete=models.CASCADE, related_name='items')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fridge_items')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    added_date = models.DateField(auto_now_add=True)
    image_url = models.URLField(max_length=200, null=True, blank=True)  # 新增字段

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    space = models.ForeignKey(FridgeSpace, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ('user', 'space')

    def __str__(self):
        return f"{self.user} subscribed to {self.space}"
