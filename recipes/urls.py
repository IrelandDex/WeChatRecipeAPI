from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, UserFavoriteViewSet,SmartRecipeViewSet

router = DefaultRouter()
router.register(r'', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'user_favorites', UserFavoriteViewSet)
router.register(r'smart_recipe', SmartRecipeViewSet, basename='smartrecipe')

urlpatterns = [
    path('', include(router.urls)),
]