from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Ingredient, Recipe, Tag


class RequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_ingredients = False
        for form in self.forms:
            if form.cleaned_data.get('ingredient'):
                has_ingredients = True
                break
        if not has_ingredients:
            raise ValidationError('At least one ingredient must be selected.')


class RecipeIngredientInline(admin.StackedInline):
    model = Recipe.ingredients.through
    formset = RequiredInlineFormSet
    autocomplete_fields = ['ingredient']
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('name', 'author__username',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('show_favorited',)
    inlines = (RecipeIngredientInline,)

    def show_favorited(self, recipe):
        return recipe.users_favorite.count()

    show_favorited.short_description = 'Добавили в избранное (раз)'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
