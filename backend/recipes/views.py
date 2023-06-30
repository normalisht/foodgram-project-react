import io
from datetime import datetime

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from users.utils import post_delete_action
from .models import Tag, Ingredient, Recipe, RecipeIngredient
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
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return post_delete_action(request, recipe, 'shopping_cart',
                                  RecipeShortSerializer)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients_amount: dict = (
            RecipeIngredient.objects
            .filter(recipe__in=request.user.shopping_cart.all())
            .select_related('ingredient')
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )

        w, h = A4
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setFont('Manrope', 14)
        pdf.drawString(
            25, h - 35,
            f"Список покупок от {datetime.today().strftime('%d.%m.%y')}"
        )  # TODO: Кешировать дату
        for index, ingredient in enumerate(ingredients_amount):
            pdf.drawString(
                25, h - 57 - (index * 22),
                f"{ingredient.get('ingredient__name')} - "
                f"{ingredient.get('amount')} "
                f"({ingredient.get('ingredient__measurement_unit')})"
            )
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename="shopping_cart.pdf")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        tags=self.request.data.get('tags'),
                        ingredients=self.request.data.get('ingredients'))

    def perform_update(self, serializer):
        self.perform_create(serializer)
