from django.db import models

from user.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32)
    color = models.CharField(max_length=8)
    slug = models.SlugField(max_length=32)


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    measurement_unit = models.CharField(max_length=16)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField()
    cooking_time = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               related_name='recipe_ingredient_model',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='recipe_ingredient_model',
                                   on_delete=models.CASCADE)
    amount = models.IntegerField()


class UserFavoriteRecipe(models.Model):
    user = models.ForeignKey(User, related_name='favorite_recipe',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='favorite_recipe',
                               on_delete=models.CASCADE)
