from rest_framework import serializers

from users.models import User
from users.serializers import UserProfileSerializer
from users.utils import is_subscribed
from .fields import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .utils import recipe_ingredients_connection, recipe_tags_connection
from .validators import UniqueAttrValidator


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
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
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient_model'
    )
    author = UserProfileSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'cooking_time', 'ingredients',
                  'tags', 'author', 'is_favorited', 'is_in_shopping_cart')
        validators = [
            UniqueAttrValidator(
                queryset=Recipe.objects.all(),
                field='recipe_ingredient_model',
                attrs='ingredient__id',
                message='Recipe ingredients cannot be duplicated'
            )
        ]

    def get_is_favorited(self, recipe):
        return recipe.users_favorites.filter(
            id=self.context['request'].user.id
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        return recipe.users_shopping_carts.filter(
            id=self.context['request'].user.id
        ).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredient_model')
        tags = self.initial_data.get('tags')

        recipe = Recipe.objects.create(**validated_data)

        recipe_tags_connection(recipe, tags)
        recipe_ingredients_connection(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.recipe_ingredient_model.all().delete()

        recipe_tags_connection(recipe, self.initial_data.get('tags'))
        recipe_ingredients_connection(
            recipe, validated_data.pop('recipe_ingredient_model')
        )

        return super().update(recipe, validated_data)


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
