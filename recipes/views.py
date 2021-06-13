import csv
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from foodgram.settings import POSTS_PER_PAGE
from users.models import Follow

from .forms import RecipeCreateForm, RecipeForm, UserEditForm
from .models import Favorite, Recipe, ShoppingList, Tag, User
from .utilities import *


def index(request):
    """Главная страница"""
    tags_list_filter, recipe_list, all_tags = get_tags_filter(request)
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "paginator": paginator,
            "page": page,
            "all_tags": all_tags,
        },
    )


def recipe_view(request, recipe_id):
    """Страница отдельного рецепта"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {"recipe": recipe}
    return render(request, "recipe.html", context)


def profile(request, username):
    """Профиль пользователя"""
    author = get_object_or_404(User, username=username)
    tags_list_filter, recipe_list, all_tags = get_tags_filter(request)
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
        "all_tags": all_tags,
        "author": author,
    }
    return render(request, "profile.html", context)


@login_required
def profile_edit(request, username):
    """ "Редактирование профиля"""
    user_profile = get_object_or_404(User, username=username)
    if request.user != user_profile:
        return redirect("profile", username=user_profile.username)
    form = UserEditForm(request.POST or None, instance=user_profile)
    if form.is_valid():
        form.save()
        return redirect("profile", username=user_profile.username)
    return render(request, "profile_edit.html", {"form": form})


@login_required()
def new_recipe(request):
    """Создание нового рецепта"""
    all_tags = Tag.objects.all()
    form = RecipeCreateForm(request.POST or None, files=request.FILES or None)
    is_new_recipe = True
    all_tags = Tag.objects.all()
    if form.is_valid():
        recipe = save_recipe(request, form)
        return redirect(to=recipe_view, recipe_id=recipe.id)
    context = {
        "form": form,
        "all_tags": all_tags,
        "is_new_recipe": is_new_recipe,
    }
    return render(request, "new_recipe.html", context)


@login_required
def recipe_edit(request, recipe_id):
    """Редактировать рецепт."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    all_tags = Tag.objects.all()
    if request.user != recipe.author and not request.user.is_staff:
        return redirect(to=recipe_view, recipe_id=recipe_id)

    form = RecipeForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    if form.is_valid():
        recipe.ingredient.clear()
        form.save()
        ingredients = get_ingredients(request)
        add_ingredients_to_recipe(ingredients, recipe)
        tags_post = get_tags(request)
        recipe.tag.set(tags_post)
        return redirect(to=recipe_view, recipe_id=recipe_id)
    context = {"form": form, "recipe": recipe, "all_tags": all_tags}
    return render(request, "new_recipe.html", context)


@login_required
def recipe_delete(request, username, recipe_id):
    """Удаление рецепта"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect("recipe", username=username, recipe_id=recipe_id)
    recipe.delete()
    return redirect("profile", username=username)


@login_required
def follow_index(request):
    """Страница подписок"""
    subscriptions = User.objects.filter(following__user=request.user).annotate(
        recipe_count=Count("recipes")
    )
    recipe = {}
    for sub in subscriptions:
        recipe[sub] = Recipe.objects.filter(author=sub)
    paginator = Paginator(subscriptions, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {
            "paginator": paginator,
            "page": page,
            "recipe": recipe,
        },
    )


@login_required
@require_http_methods(["POST", "DELETE"])
def subscriptions(request, author_id):
    """API view для выполнения подписок"""
    if request.method == "POST":
        author_id = json.loads(request.body).get("id")
        author = get_object_or_404(User, id=author_id)

        obj, created = Follow.objects.get_or_create(
            user=request.user, author=author
        )

        if request.user == author or not created:
            return JsonResponse({"success": False})
        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        author = get_object_or_404(User, id=author_id)

        removed = Follow.objects.filter(
            user=request.user, author=author
        ).delete()

        if removed:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})


@login_required()
@require_http_methods("DELETE")
def delete_subscription(request, author_id):
    """API view для удаления подписок"""
    data = {"success": "true"}
    follow = get_object_or_404(
        Follow, user__username=request.user.username, author__id=author_id
    )
    if not follow:
        data["success"] = "false"
    follow.delete()
    return JsonResponse(data)


@login_required
def favorites(request):
    """Страница мои избранные"""
    tags_list_filter, recipe_list, all_tags = get_tags_filter(request)
    recipe_list = (
        Recipe.objects.filter(in_user_favorites__user=request.user)
        .filter(tag__value__in=tags_list_filter)
        .distinct()
    )
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "paginator": paginator,
        "page": page,
        "all_tags": all_tags,
    }
    return render(request, "favorites.html", context)


@login_required
def shop_list(request):
    """Отображение страницы со списком покупок."""
    if request.GET:
        recipe_id = request.GET.get("recipe_id")
        ShoppingList.objects.filter(recipe__id=recipe_id).delete()
    purchases = Recipe.objects.filter(shop_list__user=request.user)
    return render(
        request,
        "shop_list.html",
        {
            "purchases": purchases,
        },
    )


@login_required
@require_http_methods(["POST", "DELETE"])
def change_favorites(request, recipe_id):
    """API view добавлени и удаление из избранного"""
    if request.method == "POST":
        recipe_id = json.loads(request.body).get("id")
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        obj, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe
        )

        if not created:
            return JsonResponse({"success": False})
        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})


@login_required
@require_http_methods(["POST", "DELETE"])
def purchases(request, recipe_id):
    """API view добавление и удаление покупок из корзины"""
    if request.method == "POST":
        recipe_id = json.loads(request.body).get("id")
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        obj, created = ShoppingList.objects.get_or_create(
            user=request.user, recipe=recipe
        )

        if not created:
            return JsonResponse({"success": False})
        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        removed = ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})


@login_required
def get_purchases(request):
    """Скачать лист покупок."""
    recipes = Recipe.objects.filter(shop_list__user=request.user)

    ing = {}

    for recipe in recipes:
        ingredients = recipe.ingredient.values_list("title", "dimension")
        amount = recipe.recipe_ingredients.values_list("quantity", flat=True)

        for num in range(len(ingredients)):
            title: str = ingredients[num][0]
            dimension: str = ingredients[num][1]
            quantity: int = amount[num]

            if title in ing.keys():
                ing[title] = [ing[title][0] + quantity, dimension]
            else:
                ing[title] = [quantity, dimension]

    response = HttpResponse(content_type="txt/csv")
    response["Content-Disposition"] = 'attachment; filename="shop_list.doc"'
    writer = csv.writer(response)

    for key, value in ing.items():
        writer.writerow([f"{key} ({value[1]}) - {value[0]}"])

    return response


def page_not_found(request, exception):
    """Функция страницы 404"""
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    """Функция страницы 500"""
    return render(request, "misc/500.html", status=500)
