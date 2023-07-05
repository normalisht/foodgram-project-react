import re

from django.db.utils import IntegrityError
from rest_framework import serializers

from .models import RecipeIngredient


def recipe_tags_connection(recipe, tags):
    """Добавляет теги к рецепту."""
    try:
        recipe.tags.set(tags)
    except IntegrityError as error:
        incorrect_id = re.findall('\(tag_id\)=\(\d+\)', str(error))[0]
        raise serializers.ValidationError(
            f'Not found {incorrect_id}'
        )


def recipe_ingredients_connection(recipe, ingredients):
    """Добавляет ингредиенты к рецепту."""
    recipe_ingredients = []
    for ingredient_data in ingredients:
        ingredient = ingredient_data.get('ingredient')
        recipe_ingredients.append(
            RecipeIngredient(
                ingredient_id=ingredient.get('id'), recipe=recipe,
                amount=ingredient_data.get('amount')
            )
        )
    try:
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
    except IntegrityError as error:
        incorrect_id = re.findall('\(ingredient_id\)=\(\d+\)', str(error))[0]
        raise serializers.ValidationError(
            f'Not found {incorrect_id}'
        )
