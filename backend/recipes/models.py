from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=32, db_index=True,
                            verbose_name='Название')
    color = models.CharField(max_length=8, verbose_name='Цвет (HEX код)')
    slug = models.SlugField(max_length=32)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(max_length=64, db_index=True,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=16,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE,
        db_index=True, verbose_name='Автор'
    )
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(Tag, db_index=True, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='RecipeIngredient'
    )
    users_favorites = models.ManyToManyField(
        User, blank=True, related_name='favorite_recipes',
        verbose_name='Избранное у ...'
    )
    users_shopping_carts = models.ManyToManyField(
        User, blank=True, related_name='shopping_cart',
        verbose_name='В списке покупок у ...'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name}: {self.author.username}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name='recipe_ingredient_model',
        on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, related_name='recipe_ingredient_model',
        on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(verbose_name='Кол-во')

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name}'
