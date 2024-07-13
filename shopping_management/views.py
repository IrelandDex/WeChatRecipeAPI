from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import ShoppingItem
from .serializers import ShoppingItemSerializer

class ShoppingItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 获取当前用户的所有购物项
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='batch-create')
    def batch_create(self, request):
        items_data = request.data.get('items', [])
        if not items_data:
            return Response({'detail': 'Items data is required.'}, status=status.HTTP_400_BAD_REQUEST)

        for item_data in items_data:
            item_data['user'] = request.user.id
        serializer = ShoppingItemSerializer(data=items_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update-purchased')
    def update_purchased(self, request, pk=None):
        is_purchased = request.data.get('is_purchased')
        if is_purchased is None:
            return Response({'detail': 'is_purchased status is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = self.queryset.get(id=pk, user=self.request.user)
        except ShoppingItem.DoesNotExist:
            raise NotFound('Shopping item not found.')

        item.is_purchased = is_purchased
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='batch-delete')
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'detail': 'IDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        items = self.queryset.filter(id__in=ids, user=self.request.user)
        if not items.exists():
            return Response({'detail': 'No items found or no permission to delete these items.'}, status=status.HTTP_404_NOT_FOUND)

        items.delete()
        return Response({'detail': 'Items deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
