from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from .models import CustomUser
from .serializers import PhoneLoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])  # 确保允许匿名访问
def wechat_login(request):
    openid = request.META.get('HTTP_X_WX_OPENID')
    if not openid:
        return Response({'error': 'Failed to get openid from request headers'}, status=400)

    # 查找或创建用户
    user, created = CustomUser.objects.get_or_create(wechat_openid=openid, defaults={'username': openid})

    # 生成JWT token
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    return Response({'token': token})


@api_view(['POST'])
@permission_classes([AllowAny])  # 确保允许匿名访问
def phone_login(request):
    serializer = PhoneLoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(phone_number=phone_number, username=phone_number)
            user.set_password(password)
            user.save()

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response({'token': token})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
