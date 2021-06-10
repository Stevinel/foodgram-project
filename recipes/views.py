import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Tag, User, ShoppingList, Ingredient, IngredientItem
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import RecipeCreateForm
from users.models import Follow
from django.http import JsonResponse
from .utils import get_tag

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import  JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from .forms import RecipeCreateForm
from .models import ( Favorite, Ingredient, Recipe,
                     Tag, User)




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

def recipe_view(request, slug):
    """Страница отдельного рецепта"""
    recipe = get_object_or_404(Recipe, slug=slug)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)

def profile(request, username):
    """Профиль пользователя"""
    author = get_object_or_404(User, username=username)
    recipe = author.recipes.all()
    tags_values = request.GET.getlist('filters')
    if tags_values:
        recipe = recipe.filter(tag__title__in=tags_values).all()
    tags = Tag.objects.all()
    paginator = Paginator(recipe, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = request.user.is_authenticated and request.user != author

    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
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
        print(ingredient_item)
        ingredient_item.save()
    for i in tags_post:
        tag = get_object_or_404(Tag, title=i)
        recipe.tag.add(tag)
    form.save_m2m()
    return redirect('index')





def recipe_edit(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    if request.user != recipe.author:
        return render(request, 'forbidden.html')
    ingredients = recipe.ingredient.all()
    tags = Tag.objects.all()
    form = RecipeCreateForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe
    )
    tags_post = get_tag(request)
    ingredient_names = request.POST.getlist('nameIngredient')
    ingredient_units = request.POST.getlist('unitsIngredient')
    amount = request.POST.getlist('valueIngredient')
    image_name = recipe.image.name.split('/')[1]
    context = {'form': form, 'tags': tags, 'ingredients': ingredients,
               'recipe': recipe, 'image_name': image_name}
    if not form.is_valid():
        return render(request, 'new_recipe.html', context)
    form.save()
    products_num = len(ingredient_names)
    new_ingredients = []
    IngredientItem.objects.filter(recipe__slug=slug).delete()
    for i in range(products_num):
        product = Ingredient.objects.get(title=ingredient_names[i],
                                         dimension=ingredient_units[i])
        new_ingredients.append(
            IngredientItem(recipe=recipe, ingredients=product, count=amount[i])
        )
    IngredientItem.objects.bulk_create(new_ingredients)
    recipe.tag.clear()
    for i in tags_post:
        tag = get_object_or_404(Tag, title=i)
        recipe.tag.add(tag)
    return redirect('index')



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
def subscription(request, author_id):

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


@login_required()
def shop_list(request):
    user = request.user
    my_shop_list = ShoppingList.objects.filter(user=user).first()
    recipes = None
    if my_shop_list:
        recipes = my_shop_list.recipes.all()
    return render(
        request,
        template_name='shop_list.html',
        context={'recipes': recipes}
    )


