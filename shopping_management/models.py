from django.db import models
from custom_users.models import CustomUser

class ShoppingItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shopping_items')
    name = models.CharField(max_length=100)
    is_purchased = models.BooleanField(default=False)  # 是否已购买
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
