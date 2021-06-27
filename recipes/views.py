import csv
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from foodgram.settings import POSTS_PER_PAGE

from .forms import RecipeCreateForm, UserEditForm
from .models import Favorite, Follow, Recipe, ShoppingList, Tag, User
from .utilities import get_tags_filter, save_recipe

JSON_RESPONSE_FALSE = JsonResponse({"success": False})
JSON_RESPONSE_TRUE = JsonResponse({"success": True})


def index(request):
    """Главная страница"""
    active_tags, recipe_list, all_tags = get_tags_filter(request)
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "paginator": paginator,
            "page": page,
            "active_tags": active_tags,
        },
    )


def recipe_view(request, recipe_id):
    """Страница отдельного рецепта"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    author = recipe.author
    context = {"recipe": recipe, "author": author}
    return render(request, "recipe.html", context)


def profile(request, username):
    """Профиль пользователя"""
    author = get_object_or_404(User, username=username)
    active_tags, recipe_list, all_tags = get_tags_filter(request)
    recipe_list = recipe_list.filter(author=author.id)
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
        "active_tags": active_tags,
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
    form = RecipeCreateForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        recipe = save_recipe(request, form)
        return redirect(to=recipe_view, recipe_id=recipe.id)
    context = {
        "form": form,
    }
    return render(request, "new_recipe.html", context)


@login_required
def recipe_edit(request, recipe_id):
    """Редактировать рецепт."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect(to=recipe_view, recipe_id=recipe_id)

    form = RecipeCreateForm(
        request.POST or None, files=request.FILES or None, instance=recipe
    )
    if form.is_valid():
        recipe.ingredient.clear()
        recipe = save_recipe(request, form)
        return redirect(to=recipe_view, recipe_id=recipe_id)

    image_name = recipe.image.name.split("/")[1]
    all_tags = Tag.objects.all()
    context = {
        "form": form,
        "recipe": recipe,
        "all_tags": all_tags,
        "image_name": image_name,
    }
    return render(request, "new_recipe.html", context)


@login_required
def recipe_delete(request, username, recipe_id):
    """Удаление рецепта"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author and not request.user.is_superuser:
        return redirect("recipe", username=username, recipe_id=recipe_id)
    recipe.delete()
    return redirect("profile", username=username)


@login_required
def follow_index(request):
    """Страница подписок"""
    subscriptions = User.objects.filter(following__user=request.user)
    paginator = Paginator(subscriptions, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {
            "paginator": paginator,
            "page": page,
        },
    )


@login_required
@require_http_methods(["POST", "DELETE"])
def subscriptions(request, author_id):
    """API view для выполнения подписок"""
    if request.method == "POST":
        author_id = json.loads(request.body).get("id")
        author = get_object_or_404(User, id=author_id)

        if author == request.user:
            return JSON_RESPONSE_FALSE

        Follow.objects.get_or_create(user=request.user, author=author)
        return JSON_RESPONSE_TRUE

    elif request.method == "DELETE":
        author = get_object_or_404(User, id=author_id)

        removed = Follow.objects.filter(
            user=request.user, author=author
        ).delete()

        if removed:
            return JSON_RESPONSE_TRUE
        return JSON_RESPONSE_FALSE


@login_required()
@require_http_methods("DELETE")
def delete_subscription(request, author_id):
    """API view для удаления подписок"""
    follow = get_object_or_404(
        Follow, user__username=request.user.username, author__id=author_id
    )
    if not follow:
        JSON_RESPONSE_TRUE = JSON_RESPONSE_FALSE
    follow.delete()
    return JSON_RESPONSE_TRUE


@login_required
def favorites(request):
    """Страница мои избранные"""
    active_tags, _, all_tags = get_tags_filter(request)
    request_tags = request.GET.getlist("filters")
    recipe_list = Recipe.objects.filter(
        in_user_favorites__user=request.user, tag__value__in=request_tags
    ).distinct()
    paginator = Paginator(recipe_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "paginator": paginator,
        "page": page,
        "active_tags": active_tags,
    }
    return render(request, "favorites.html", context)


@login_required
def shop_list(request):
    """Отображение страницы со списком покупок."""
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
            return JSON_RESPONSE_FALSE
        return JSON_RESPONSE_TRUE

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JSON_RESPONSE_TRUE
        return JSON_RESPONSE_FALSE


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
            return JSON_RESPONSE_FALSE
        return JSON_RESPONSE_TRUE

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        removed = ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JSON_RESPONSE_TRUE
        return JSON_RESPONSE_FALSE


@login_required
def download_purchases(request):
    """Скачать лист покупок."""
    recipes = (
        Recipe.objects.filter(shop_list__user=request.user)
        .order_by("ingredient__title")
        .values("ingredient__title", "ingredient__dimension")
        .annotate(total_quantity=Sum("recipe_ingredients__quantity"))
    )

    response = HttpResponse(content_type="txt/csv")
    response["Content-Disposition"] = 'attachment; filename="shop_list.txt"'
    writer = csv.writer(response)

    for recipe in recipes:
        writer.writerow(
            [
                f"{recipe['ingredient__title']} - {recipe['total_quantity']}"
                f"{recipe['ingredient__dimension']}"
            ]
        )
    return response


def page_not_found(request, exception):
    """Функция страницы 404"""
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    """Функция страницы 500"""
    return render(request, "misc/500.html", status=500)
