from django.db.models import BooleanField, Case, When
from django_filters.rest_framework import (BooleanFilter, FilterSet,
                                           ModelMultipleChoiceFilter)
from rest_framework.filters import SearchFilter
from .models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        lookup_expr='exact', queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited',)

    def filter_is_favorited(self, queryset, name, value):
        # ChatGpt помог, но наверное должен быть способ проще
        return queryset.annotate(
            is_favorited=Case(
                When(users_favorite=self.request.user, then=True),
                default=False,
                output_field=BooleanField()
            )
        ).filter(is_favorited=value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.annotate(
            is_in_shopping_cart=Case(
                When(users_shopping_carts=self.request.user, then=True),
                default=False,
                output_field=BooleanField()
            )
        ).filter(is_in_shopping_cart=value)
