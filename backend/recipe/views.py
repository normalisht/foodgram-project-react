from typing import Type

from django.db import models
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
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
        return post_delete_action(request, Recipe, pk, 'favorite_recipes')

    @action(detail=True, methods=['post', 'delete'])
    def shopping_card(self, request, pk=None):
        return post_delete_action(request, Recipe, pk, 'shopping_card')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        tags=self.request.data.get('tags'),
                        ingredients=self.request.data.get('ingredients'))

    def perform_update(self, serializer):
        self.perform_create(serializer)


def post_delete_action(request, model: Type[models.Model], model_obj_pk: int,
                       related_name: str):
    """Реализует post и delete методы для связи многие-ко-многим.
    Связь многие-ко-многим между авторизированным пользователем и таблицей
    model. "related_name" - название связующего поля в таблице User."""

    user = request.user
    obj = model.objects.get(pk=model_obj_pk)

    if request.method == 'POST':
        if getattr(user, related_name).filter(id=obj.id).exists():
            return Response(
                {'error': 'This recipe already in shopping card'},
                status=status.HTTP_400_BAD_REQUEST
            )
        getattr(user, related_name).add(obj)
        serializer = RecipeShortSerializer(obj, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    getattr(user, related_name).remove(obj)
    return Response(status=status.HTTP_204_NO_CONTENT)