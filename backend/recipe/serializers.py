from django.db.models import ObjectDoesNotExist
from rest_framework import serializers

from user.models import User
from user.serializers import UserProfileSerializer
from user.utils import is_subscribed
from .fields import Base64ImageField
from .models import Tag, Ingredient, Recipe, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # Почему без этой строчки нет id в ответе?

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    author = UserProfileSerializer(read_only=True)

    # TODO: Добавить поля is_favorited и is_in_shopping_cart

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'cooking_time', 'tags',
                  'ingredients', 'author',)

    def get_ingredients(self, recipe):
        serializer = RecipeIngredientSerializer(
            data=recipe.recipe_ingredient_model.all(),
            many=True
        )
        serializer.is_valid()
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        recipe_tags_connection(recipe, tags)
        recipe_ingredients_connection(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        # Согласно спецификации, обновление рецептов
        # должно быть реализовано через PATCH
        recipe.tags.remove()
        RecipeIngredient.objects.filter(recipe=recipe).delete()

        recipe_tags_connection(recipe, validated_data.pop('tags'))
        recipe_ingredients_connection(recipe,
                                      validated_data.pop('ingredients'))

        for field, value in validated_data.items():
            setattr(recipe, field, value)

        return recipe


def recipe_tags_connection(recipe, tags):
    """Добавляет теги к рецепту."""

    for tag_id in tags:
        try:
            tag = Tag.objects.get(id=tag_id)
            recipe.tags.add(tag)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                f'Tag with {tag_id=} not found'
            )


def recipe_ingredients_connection(recipe, ingredients):
    """Добавляет ингредиенты к рецепту."""

    for ingredient in ingredients:
        try:
            ingredient_obj = Ingredient.objects.get(
                id=ingredient.get('id')
            )
            RecipeIngredient.objects.create(
                ingredient=ingredient_obj, recipe=recipe,
                amount=ingredient.get('amount')
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                f'Ingredient with id={ingredient.get("id")} not found'
            )


# Надо расположить в приложении users, но тогда получается циклический импорт,
# который я не знаю как обойти
class UserFullDataSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'recipes', 'recipes_count', 'is_subscribed')

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_is_subscribed(self, author):
        return is_subscribed(self.context['request'].user, author)
