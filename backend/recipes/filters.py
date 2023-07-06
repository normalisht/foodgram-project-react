from django_filters.rest_framework import (
    BooleanFilter, FilterSet, ModelMultipleChoiceFilter, ModelChoiceFilter
)

from users.models import User
from .models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        lookup_expr='exact', queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    author = ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, *args):
        if self.request.user.is_authenticated:
            return queryset.filter(users_favorites=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, *args):
        if self.request.user.is_authenticated:
            return queryset.filter(users_shopping_carts=self.request.user)
        return queryset
