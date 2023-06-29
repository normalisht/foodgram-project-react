from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .models import Tag, Ingredient, Recipe, UserFavoriteRecipe
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
        recipe = Recipe.objects.get(pk=pk)

        if request.method == 'POST':
            _, create = UserFavoriteRecipe.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not create:
                return Response(
                    {'error': 'This recipe already in favorite list'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        UserFavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        tags=self.request.data.get('tags'),
                        ingredients=self.request.data.get('ingredients'))

    def perform_update(self, serializer):
        self.perform_create(serializer)
