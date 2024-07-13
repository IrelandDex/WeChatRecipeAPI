# fridge_management/views.py
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import FridgeItem, FridgeSpace, Subscription
from .serializers import FridgeItemSerializer, FridgeSpaceSerializer, SubscriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.conf import settings


class FridgeSpaceViewSet(viewsets.ModelViewSet):
    queryset = FridgeSpace.objects.all()
    serializer_class = FridgeSpaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        space = serializer.save(user=self.request.user)
        # Automatically subscribe the user to the newly created space
        Subscription.objects.create(user=self.request.user, space=space)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('You do not have permission to delete this space.')
        instance.delete()


class FridgeItemViewSet(viewsets.ModelViewSet):
    queryset = FridgeItem.objects.all()
    serializer_class = FridgeItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.query_params
        space_id = query_params.get('space', None)

        if space_id:
            try:
                space_id = int(space_id)  # 确保 space_id 是整数
            except ValueError:
                return self.queryset.none()  # 如果 space_id 不是有效的整数，返回空的查询集
            subscribed_spaces = Subscription.objects.filter(user=user).values_list('space_id', flat=True)
            if space_id in subscribed_spaces:
                return self.queryset.filter(space_id=space_id)
            else:
                return self.queryset.none()
        else:
            return self.queryset.filter(space__user=user)

    def perform_create(self, serializer):
        space_id = self.request.data.get('space')
        try:
            space = FridgeSpace.objects.get(id=space_id)
        except FridgeSpace.DoesNotExist:
            raise ValidationError({'error': 'Space does not exist.'})

        if not Subscription.objects.filter(user=self.request.user,
                                           space=space).exists() and space.user != self.request.user:
            raise ValidationError({'error': 'You do not have permission to add items to this space.'})

        image = self.request.FILES.get('image')
        if image:
            image_url = self.upload_to_s3(image)
            if image_url:
                serializer.save(image_url=image_url, space=space, user=self.request.user)
            else:
                raise ValidationError({'error': 'Failed to upload image.'})
        else:
            serializer.save(space=space, user=self.request.user)

    def perform_update(self, serializer):
        space_id = self.request.data.get('space')
        if not space_id:
            raise ValidationError({'error': 'Space field is required.'}, )

        try:
            space = FridgeSpace.objects.get(id=space_id)
        except FridgeSpace.DoesNotExist:
            raise ValidationError({'error': 'Space does not exist.'})

        if not Subscription.objects.filter(user=self.request.user,
                                           space=space).exists() and space.user != self.request.user:
            raise PermissionDenied('You do not have permission to update items in this space.')

        image = self.request.FILES.get('image')
        if image:
            image_url = self.upload_to_s3(image)
            if image_url:
                serializer.save(image_url=image_url, space=space)
            else:
                raise ValidationError({'error': 'Failed to update image.'})
        else:
            serializer.save(space=space)

    def upload_to_s3(self, file):
        pass
        # s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        #                   region_name=settings.AWS_S3_REGION_NAME)
        # try:
        #     s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
        #     url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file.name}"
        #     return url
        # except NoCredentialsError:
        #     return None


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        share_key = self.request.data.get('share_key')
        try:
            space = FridgeSpace.objects.get(share_key=share_key)
            if Subscription.objects.filter(user=self.request.user, space=space).exists():
                raise ValidationError({'error': 'You are already subscribed to this space.'})
            serializer.save(user=self.request.user, space=space)
        except FridgeSpace.DoesNotExist:
            raise ValidationError({'error': 'Invalid share key.'})

    def perform_destroy(self, instance_id):
        try:
            # 在删除操作中，通过未过滤的查询集获取实例
            instance = Subscription.objects.get(id=instance_id)
        except Subscription.DoesNotExist:
            raise NotFound('Subscription not found.')

        if instance.user != self.request.user:
            raise PermissionDenied('You do not have permission to unsubscribe from this space.')

        space = instance.space
        if space.user == self.request.user:
            raise PermissionDenied('Space creators can only delete, not unsubscribe.')

        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance_id = kwargs.get('pk')
        self.perform_destroy(instance_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
