from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient, CookStep, UserFavorite

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'title']
        extra_kwargs = {
            'title': {'validators': []},
        }

class CookStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookStep
        fields = ['id', 'title', 'content', 'image_url']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount', 'is_main']

class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    ingredients = RecipeIngredientSerializer(many=True)
    cook_steps = CookStepSerializer(many=True)
    is_favored = serializers.SerializerMethodField()
    relevance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'author', 'cover_img', 'story_content', 'recipe_type', 'is_favored',
            'seo_title', 'seo_keywords', 'seo_description', 'release_date', 'recipe_long_img', 'ingredients', 'cook_steps', 'relevance'
        ]

    def get_is_favored(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return UserFavorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        cook_steps_data = validated_data.pop('cook_steps')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            ingredient_obj, created = Ingredient.objects.get_or_create(title=ingredient['title'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient_data['amount'],
                is_main=ingredient_data['is_main']
            )

        for step_data in cook_steps_data:
            CookStep.objects.create(recipe=recipe, **step_data)

        return recipe

class RecipeListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'author', 'cover_img']

class UserFavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ['id', 'user', 'recipe']
