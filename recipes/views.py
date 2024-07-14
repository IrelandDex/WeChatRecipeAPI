from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db.models import Q, Count
from .models import Recipe, Ingredient, RecipeIngredient, CookStep, UserFavorite
from .serializers import RecipeSerializer, IngredientSerializer, UserFavoriteSerializer, RecipeListSerializer
from rest_framework.views import APIView


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmalldResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 20


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = StandardResultsSetPagination  # 使用自定义的分页类

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', '')
        ingredients = request.query_params.getlist('ingredients')

        if ingredients:
            recipes = self.queryset.filter(
                Q(title__icontains=query) | Q(story_content__icontains=query)
            ).annotate(
                relevance=Count('recipe_ingredients__ingredient',
                                filter=Q(recipe_ingredients__ingredient__id__in=ingredients))
            ).order_by('-relevance', '-release_date')
        else:
            recipes = self.queryset.filter(
                Q(title__icontains=query) | Q(story_content__icontains=query)
            ).order_by('-release_date')

        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user-favorites')
    def user_favorites(self, request):
        user = request.user
        favorites = UserFavorite.objects.filter(user=user)
        recipes = [favorite.recipe for favorite in favorites]
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = StandardResultsSetPagination  # 使用自定义的分页类

    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        ingredient, created = Ingredient.objects.get_or_create(title=title)
        if not created:
            return Response({'detail': 'Ingredient already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().perform_create(serializer)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    queryset = UserFavorite.objects.all()
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SmartRecipeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SmalldResultsSetPagination  # 使用自定义的分页类

    def get_queryset(self):
        ingredient_ids = self.request.query_params.getlist('ingredients')
        if not ingredient_ids:
            return Recipe.objects.none()  # 返回空的 QuerySet

        return Recipe.objects.filter(
            ingredients__ingredient_id__in=ingredient_ids
        ).annotate(
            relevance=Count('ingredients__ingredient_id')
        ).order_by('-relevance', '-release_date').distinct()

    def list(self, request, *args, **kwargs):
        ingredient_ids = request.query_params.getlist('ingredients')
        if not ingredient_ids:
            return Response({"error": "No ingredients provided"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
