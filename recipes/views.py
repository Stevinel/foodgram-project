import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Tag, User, ShoppingList, Ingredient, IngredientItem
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import RecipeCreateForm
from users.models import Follow
from django.http import JsonResponse
from .utils import get_tag


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

@login_required()
def new_recipe(request):
    form = RecipeCreateForm(request.POST or None, files=request.FILES or None)
    tags = Tag.objects.all()
    ingredient_names = request.POST.getlist('nameIngredient')
    ingredient_units = request.POST.getlist('unitsIngredient')
    amount = request.POST.getlist('valueIngredient')
    tags_post = get_tag(request)
    is_new_recipe = True
    if not form.is_valid():
        context = {'form': form, 'tags': tags, 'is_new_recipe': is_new_recipe}
        return render(request, 'new_recipe.html', context)
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    products_num = len(ingredient_names)
    ingredients = []
    for i in range(products_num):
        product = Ingredient.objects.get(
            title=ingredient_names[i],
            dimension=ingredient_units[i]
        )
        ingredients.append(
            IngredientItem(recipe=recipe, ingredients=product, count=amount[i])
        )
    IngredientItem.objects.bulk_create(ingredients)
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



def get_ingredients(request):
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
    """Функция страницы подписок""" 
    recipe_list = Recipe.objects.filter(author__following__user=request.user) 
    paginator = Paginator(recipe_list, 10) 
    page_number = request.GET.get("page") 
    page = paginator.get_page(page_number) 
    context = { 
        "page": page, 
        "paginator": paginator, 
        "recipe_list": recipe_list
    } 
    return render(request, "follow.html", context) 

@login_required 
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

@login_required
def favorites(request):
    favorite_list = Recipe.objects.filter(author__following__user=request.user)
    paginator = Paginator(favorite_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator}
    return render(request, 'favorites.html', context)

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


