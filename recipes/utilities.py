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
    all_tags = Tag.objects.all()
    request_tags = request.GET.getlist("filters")

    active_tags = {}
    for tag in all_tags:
        if tag.value in request_tags:
            active_tags[tag.value] = {
                "status": True,
                "title": tag.title,
                "color": tag.color,
            }
        else:
            active_tags[tag.value] = {
                "status": False,
                "title": tag.title,
                "color": tag.color,
            }

    if not request_tags:
        for tag in all_tags:
            request_tags.append(tag.value)

    recipe_list = (
        Recipe.objects.filter(tag__value__in=request_tags)
        .select_related("author")
        .prefetch_related("tag")
        .distinct()
    )
    return (
        active_tags,
        recipe_list,
        all_tags,
    )


def get_tags():
    all_tags = Tag.objects.all()
    tags_list = []
    for tag in all_tags:
        tags_list.append(tag.value)
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
    if recipe.author == request.user:
        recipe.author = request.user
    recipe.save()
    ingredients = get_ingredients(request)
    add_ingredients_to_recipe(ingredients, recipe)
    form.save_m2m()
    return recipe
