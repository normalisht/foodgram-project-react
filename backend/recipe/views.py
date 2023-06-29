from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from user.utils import post_delete_action
from .models import Tag, Ingredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeShortSerializer, )


class RetrieveListViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    pagination_class = None


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredient_model__ingredient'
    ).all()
    serializer_class = RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return post_delete_action(request, recipe, 'favorite_recipes',
                                  RecipeShortSerializer)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_card(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return post_delete_action(request, recipe, 'shopping_card',
                                  RecipeShortSerializer)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        tags=self.request.data.get('tags'),
                        ingredients=self.request.data.get('ingredients'))

    def perform_update(self, serializer):
        self.perform_create(serializer)
