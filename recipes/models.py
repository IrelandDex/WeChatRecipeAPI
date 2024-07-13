from django.db import models
from custom_users.models import CustomUser

class Ingredient(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes')
    cover_img = models.URLField()
    story_content = models.TextField()
    recipe_type = models.CharField(max_length=50)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    release_date = models.DateTimeField(auto_now_add=True)
    recipe_long_img = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipes')
    amount = models.CharField(max_length=50)
    is_main = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.recipe.title} - {self.ingredient.title}"

class CookStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cook_steps')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    image_url = models.URLField()

    def __str__(self):
        return self.title

class UserFavorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"
