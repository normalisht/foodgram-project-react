from rest_framework import serializers

from users.models import User
from users.serializers import UserProfileSerializer
from users.utils import is_subscribed
from .fields import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient, Tag
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


class RecipeReadSerializer(serializers.ModelSerializer):
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

    def get_is_favorited(self, recipe):
        return recipe.users_favorites.filter(
            id=self.context['request'].user.id
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        return recipe.users_shopping_carts.filter(
            id=self.context['request'].user.id
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient_model'
    )

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'cooking_time', 'ingredients',
                  'tags',)
        validators = [
            UniqueAttrValidator(
                queryset=Recipe.objects.all(),
                field='recipe_ingredient_model',
                attrs='ingredient__id',
                message='Recipe ingredients cannot be duplicated'
            )
        ]

    def validate_ingredients(self, ingredients):
        id_list = [item.get('ingredient').get('id') for item in ingredients]

        if len(id_list) > len(set(id_list)):
            raise serializers.ValidationError(
                'Ingredients cannot be repeated.'
            )

        if Ingredient.objects.filter(id__in=id_list).count() != len(id_list):
            raise serializers.ValidationError('Some ingredients not found.')

        return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredient_model')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)
        self.recipe_ingredients_connection(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.recipe_ingredient_model.all().delete()

        recipe.tags.set(validated_data.pop('tags'))
        self.recipe_ingredients_connection(
            recipe, validated_data.pop('recipe_ingredient_model')
        )

        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return RecipeReadSerializer(context=self.context
                                    ).to_representation(recipe)

    def recipe_ingredients_connection(self, recipe, ingredients):
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
        RecipeIngredient.objects.bulk_create(recipe_ingredients)


class UserFullDataSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
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

    def get_recipes(self, user):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = (user.recipes.all()[:int(limit)] if limit is not None
                   else user.recipes.all())
        return RecipeShortSerializer(recipes, many=True).data
