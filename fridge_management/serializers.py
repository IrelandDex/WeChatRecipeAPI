from rest_framework import serializers
from .models import FridgeItem, Subscription, FridgeSpace


class FridgeSpaceSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = FridgeSpace
        fields = ['id', 'name', 'share_key', 'is_owner']
        read_only_fields = ['share_key']

    def get_is_owner(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.user == request.user
        return False

class FridgeItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = FridgeItem
        fields = ['id', 'space', 'name', 'quantity', 'expiry_date', 'added_date', 'image_url', 'image']
        extra_kwargs = {'image_url': {'read_only': True}}


class SubscriptionSerializer(serializers.ModelSerializer):
    space = FridgeSpaceSerializer(read_only=True)  # 嵌套的序列化器
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'space']
        read_only_fields = ['user', 'space']
