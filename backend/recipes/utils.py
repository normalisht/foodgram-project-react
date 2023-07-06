from django.shortcuts import get_object_or_404

from users.utils import post_delete_action
from .models import Recipe
from .serializers import RecipeShortSerializer


def post_delete_action_for_recipe_obj(request, related_name: str, obj_id: int):
    recipe = get_object_or_404(Recipe, pk=obj_id)
    return post_delete_action(request, recipe, related_name,
                              RecipeShortSerializer)
