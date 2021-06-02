import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Tag, User, ShoppingList
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm
from users.models import Follow
from django.http import HttpResponse, JsonResponse

def index(request):
    """Главная страница"""
    recipe = Recipe.objects.all()
    paginator = Paginator(recipe, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    tag = Tag.objects.filter(title__in='Завтрак')
    context = {
        'page': page,
        'paginator': paginator,
        'tag': tag,
        
    }
    return render(request, "index.html", context)

def recipe_view(request, recipe_id):
    """Страница отдельного рецепта"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
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
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        return redirect("index")

    context = {
        "form": form,
        "is_new_recipe": True,
    }
    return render(request, "new_recipe.html", context)


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