from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, UserFavoriteViewSet,SmartRecipeViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'user_favorites', UserFavoriteViewSet)
router.register(r'smart_recipe', SmartRecipeViewSet, basename='smartrecipe')

urlpatterns = [
    path('', include(router.urls)),
]