from django.urls import path
from .views import wechat_login, phone_login

urlpatterns = [
    path('wechat_login/', wechat_login, name='wechat_login'),
    path('phone_login/', phone_login, name='phone_login'),
]