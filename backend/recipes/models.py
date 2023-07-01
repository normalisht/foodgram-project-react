from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32, db_index=True)
    color = models.CharField(max_length=8)
    slug = models.SlugField(max_length=32)


class Ingredient(models.Model):
    name = models.CharField(max_length=64, db_index=True)
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
    tags = models.ManyToManyField(Tag, db_index=True)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')

    # Хотел добавить эти поля в таблицу User, но ругается на циклический импорт
    users_favorite = models.ManyToManyField(User,
                                            related_name='favorite_recipes')
    users_shopping_carts = models.ManyToManyField(User,
                                                  related_name='shopping_cart')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               related_name='recipe_ingredient_model',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='recipe_ingredient_model',
                                   on_delete=models.CASCADE)
    amount = models.IntegerField()
