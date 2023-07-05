import io

from django.db.models import Sum
from django.http import FileResponse
from django.utils.timezone import localdate
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsAuthor, ReadOnly
from .filters import RecipeFilter
from .mixins import RetrieveListViewSet
from .models import Ingredient, Recipe, RecipeIngredient, Tag
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .utils2 import post_delete_action_for_recipe_obj


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredient_model__ingredient'
    ).all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAdminUser | IsAuthor | ReadOnly]

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return post_delete_action_for_recipe_obj(
            request, 'favorite_recipes', pk
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return post_delete_action_for_recipe_obj(
            request, 'shopping_cart', pk
        )

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients_amount: dict = (
            RecipeIngredient.objects
            .filter(recipe__in=request.user.shopping_cart.all())
            .select_related('ingredient')
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount_sum=Sum('amount'))
        )

        w, h = A4
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setFont('Manrope', 14)

        pdf.drawString(
            25, h - 35,
            f"Список покупок от {localdate().strftime('%d.%m.%y')}"
        )

        if not ingredients_amount:
            pdf.drawString(
                25, h - 57,
                "Ваш список покупок пуст. Пора выбирать новый рецепт!"
            )

        for index, ingredient in enumerate(ingredients_amount):
            pdf.drawString(
                25, h - 57 - (index * 22),
                f"{ingredient.get('ingredient__name')} - "
                f"{ingredient.get('amount_sum')} "
                f"({ingredient.get('ingredient__measurement_unit')})"
            )
        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True,
                            filename="shopping_cart.pdf")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
