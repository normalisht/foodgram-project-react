from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
