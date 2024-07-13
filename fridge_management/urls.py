from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FridgeSpaceViewSet, FridgeItemViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'spaces', FridgeSpaceViewSet)
router.register(r'items', FridgeItemViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('fridge/', include(router.urls)),
]
