import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Tag, User, ShoppingList, Ingredient, IngredientItem
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import RecipeCreateForm
from users.models import Follow
from django.http import HttpResponse, JsonResponse
from .utils import get_tag
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import  JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from .forms import RecipeCreateForm, RecipeForm, UserEditForm
from .models import ( Favorite, Ingredient, Recipe,
                     Tag, User)
import csv
                     




def index(request):
    tags_list = request.GET.getlist('filters')

    if tags_list == []:
        tags_list = ['breakfast', 'lunch', 'dinner']

    recipe_list = Recipe.objects.filter(
        tag__value__in=tags_list
    ).select_related(
        'author'
    ).prefetch_related(
        'tag'
    ).distinct()

    all_tags = Tag.objects.all()

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'paginator': paginator,
        'page': page,
        'all_tags': all_tags,
        'tags_list': tags_list,
    }
    )

def recipe_view(request, recipe_id):
    """Страница отдельного рецепта"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)

def profile(request, username):
    """Профиль пользователя"""
    author = get_object_or_404(User, username=username)
    tags_list = request.GET.getlist('filters')
    if tags_list == []:
        tags_list = ['breakfast', 'lunch', 'dinner']

    recipe = Recipe.objects.filter(
        tag__value__in=tags_list
    ).prefetch_related(
        'tag'
    ).distinct()

    all_tags = Tag.objects.all()
    paginator = Paginator(recipe, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = request.user.is_authenticated and request.user != author

    context = {
        'page': page,
        'paginator': paginator,
        'all_tags': all_tags,
        'author': author,
        'is_following': is_following,
    }
    return render(request, 'profile.html', context)

def get_ingredients(request):
    ingredients = {}
    for key in request.POST:
        if key.startswith('nameIngredient'):
            ing_num = key[15:]
            ingredients[request.POST[key]] = request.POST[
                                                'valueIngredient_' + ing_num]
    return ingredients

@login_required()
def new_recipe(request):
    form = RecipeCreateForm(request.POST or None, files=request.FILES or None)
    tags = Tag.objects.all()
    tags_post = get_tag(request)
    is_new_recipe = True
    if not form.is_valid():
        context = {'form': form, 'tags': tags, 'is_new_recipe': is_new_recipe}
        return render(request, 'new_recipe.html', context)
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    ingredients = get_ingredients(request)
    for title, quantity in ingredients.items():
        ingredient = Ingredient.objects.get(title=title)
        ingredient_item = IngredientItem(
            recipe=recipe,
            quantity=quantity,
            ingredient=ingredient
        )
        ingredient_item.save()
    for i in tags_post:
        tag = get_object_or_404(Tag, title=i)
        recipe.tag.add(tag)
    form.save_m2m()
    return redirect('index')


@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)
    all_tags = Tag.objects.all()
    recipe_tags = recipe.tag.values_list('value', flat=True)

    if request.user != author:
        return redirect(
            "recipe",
            recipe_id=recipe_id
        )

    if request.method == 'POST':
        form = RecipeForm(
            request.POST,
            files=request.FILES or None,
            instance=recipe
        )

        if form.is_valid():
            my_recipe = form.save(commit=False)
            my_recipe.author = request.user
            my_recipe.save()
            new_tags = get_tag(request)
            my_recipe.recipe_ingredients.all().delete()
            ingredients = get_ingredients(request)
            for title, quantity in ingredients.items():
                ingredient = Ingredient.objects.get(title=title)
                amount = IngredientItem(
                    recipe=my_recipe,
                    ingredient=ingredient,
                    quantity=quantity
                )
                amount.save()

            my_recipe.tag.set(new_tags)
            return redirect(
                'recipe',
                recipe_id=recipe.id,
            )

    form = RecipeForm(instance=recipe)
    image_name = recipe.image.name.split('/')[1]
    return render(request, "new_recipe.html", {
        'form': form,
        'recipe': recipe,
        'all_tags': all_tags,
        'recipe_tags': recipe_tags,
        'image_name':image_name,
    })

@login_required
def recipe_delete(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    author = get_object_or_404(User, id=recipe.author_id)

    if request.user != author:
        return redirect(
            "recipe",
            username=username,
            recipe_id=recipe_id
        )

    recipe.delete()
    return redirect("profile", username=username)

def ingredients(request):
    text = request.GET['query']
    ingredients = Ingredient.objects.filter(title__istartswith=text)
    ing_list = []
    for ing in ingredients:
        ing_dict = {}
        ing_dict['title'] = ing.title
        ing_dict['dimension'] = ing.dimension
        ing_list.append(ing_dict)
    return JsonResponse(ing_list, safe=False)

@login_required
def follow_index(request):
    subscriptions = User.objects.filter(
        following__user=request.user
    ).annotate(
        recipe_count=Count(
            'recipes'
        )
    )

    recipe: dict = {}
    for sub in subscriptions:
        recipe[sub] = Recipe.objects.filter(
            author=sub
        )[:3]

    paginator = Paginator(subscriptions, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {
        'paginator': paginator,
        'page': page,
        'recipe': recipe,
    }
    )

@login_required
@require_http_methods(["POST", "DELETE"])
def subscriptions(request, author_id):

    # подписаться на автора
    if request.method == "POST":
        author_id = json.loads(request.body).get('id')
        author = get_object_or_404(User, id=author_id)

        obj, created = Follow.objects.get_or_create(
            user=request.user, author=author
        )

        if request.user == author or not created:
            return JsonResponse({'success': False})

        return JsonResponse({'success': True})

    # отписаться от автора
    elif request.method == "DELETE":
        author = get_object_or_404(User, id=author_id)

        removed = Follow.objects.filter(
            user=request.user, author=author
        ).delete()

        if removed:
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})

@login_required()
@require_http_methods('DELETE')
def delete_subscription(request, author_id):
    data = {'success': 'true'}
    follow = get_object_or_404(
        Follow,
        user__username=request.user.username,
        author__id=author_id
    )
    if not follow:
        data['success'] = 'false'
    follow.delete()
    return JsonResponse(data)

@login_required
def favorites(request):
    tags_list = request.GET.getlist('filters')
    if not tags_list:
        tags_list = ['breakfast', 'lunch', 'dinner']
    all_tags = Tag.objects.all()
    recipe_list = Recipe.objects.filter(
        in_user_favorites__user=request.user
    ).filter(
        tag__value__in=tags_list
    ).distinct()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'paginator': paginator,
        'page': page,
        'all_tags': all_tags,
        'tags_list': tags_list
    }
    return render(request, 'favorites.html', context)

    

@login_required
@require_http_methods(["POST", "DELETE"])
def change_favorites(request, recipe_id):

    # добавить в избранное
    if request.method == "POST":
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(
            Recipe, pk=recipe_id
        )

        obj, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe
        )

        if not created:
            return JsonResponse({'success': False})

        return JsonResponse({'success': True})

    # удалить из изобранного
    elif request.method == "DELETE":
        recipe = get_object_or_404(
            Recipe, pk=recipe_id
        )

        removed = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


@login_required
def shop_list(request):
    """Отображение страницы со списком покупок."""
    if request.GET:
        recipe_id = request.GET.get('recipe_id')
        ShoppingList.objects.get(
            recipe__id=recipe_id
        ).delete()

    purchases = Recipe.objects.filter(shop_list__user=request.user)

    return render(request, "shop_list.html", {
        'purchases': purchases,
    }
    )

@login_required
def get_purchases(request):
    """Скачать лист покупок."""
    recipes = Recipe.objects.filter(
        shop_list__user=request.user
    )

    ing: dict = {}

    for recipe in recipes:
        ingredients = recipe.ingredient.values_list(
            'title', 'dimension'
        )
        amount = recipe.recipe_ingredients.values_list(
            'quantity', flat=True
        )

        for num in range(len(ingredients)):
            title: str = ingredients[num][0]
            dimension: str = ingredients[num][1]
            quantity: int = amount[num]

            if title in ing.keys():
                ing[title] = [ing[title][0] + quantity, dimension]
            else:
                ing[title] = [quantity, dimension]

    response = HttpResponse(content_type='txt/csv')
    response['Content-Disposition'] = 'attachment; filename="shop_list.doc"'
    writer = csv.writer(response)

    for key, value in ing.items():
        writer.writerow([f'{key} ({value[1]}) - {value[0]}'])

    return response


@login_required
@require_http_methods(["POST", "DELETE"])
def purchases(request, recipe_id):

    # добавить в список покупок
    if request.method == "POST":
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        obj, created = ShoppingList.objects.get_or_create(
            user=request.user, recipe=recipe
        )

        if not created:
            return JsonResponse({'success': False})

        return JsonResponse({'success': True})

    # удалить из списка покупок
    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        removed = ShoppingList.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if removed:
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})

@login_required
def profile_edit(request, username):
    """"Функция редактирования профиля"""
    user_profile = get_object_or_404(User, username=username)
    if request.user != user_profile:
        return redirect('profile', username=user_profile.username)
    form = UserEditForm(request.POST or None, instance=user_profile)
    if form.is_valid():
        form.save()
        return redirect('profile', username=user_profile.username)
    return render(request, 'profile_edit.html', {'form': form})