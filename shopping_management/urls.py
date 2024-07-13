from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShoppingItemViewSet

router = DefaultRouter()
router.register(r'items', ShoppingItemViewSet)

urlpatterns = [
    path('shopping/', include(router.urls)),
]
