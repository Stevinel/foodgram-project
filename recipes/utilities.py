from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Ingredient, IngredientItem, Recipe, Tag


def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith("nameIngredient"):
            ing_num = key[15:]
            ingredients[request.POST[key]] = request.POST[
                "valueIngredient_" + ing_num
            ]
    return ingredients


def get_tags_filter(request):
    tags_list = Tag.objects.values_list("value")
    tags_list_filter = request.GET.getlist("filters")
    if tags_list_filter == []:
        tags_list_filter = tags_list

    recipe_list = (
        Recipe.objects.filter(tag__value__in=tags_list_filter)
        .select_related("author")
        .prefetch_related("tag")
        .distinct()
    )

    all_tags = Tag.objects.all()

    return tags_list_filter, recipe_list, all_tags


def get_tags(request):
    tags_list = []
    for field, value in request.POST.items():
        if value == "on":
            tags_list.append(field)
    return tags_list


def ingredients(request):
    text = request.GET["query"]
    ingredients = Ingredient.objects.filter(title__istartswith=text)
    ing_list = []
    for ing in ingredients:
        ing_dict = {}
        ing_dict["title"] = ing.title
        ing_dict["dimension"] = ing.dimension
        ing_list.append(ing_dict)
    return JsonResponse(ing_list, safe=False)


def add_ingredients_to_recipe(ingredients, recipe):
    """Добавить ингредиенты в рецепт."""
    for title, quantity in ingredients.items():
        ingredient = get_object_or_404(Ingredient, title=title)
        ingredient_item = IngredientItem(
            recipe=recipe, quantity=quantity, ingredient=ingredient
        )
        ingredient_item.save()


def save_recipe(request, form):
    """Сохранить форму"""
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    ingredients = get_ingredients(request)
    add_ingredients_to_recipe(ingredients, recipe)
    form.save_m2m()
    return recipe
