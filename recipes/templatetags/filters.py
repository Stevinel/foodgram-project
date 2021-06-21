from django import template

from recipes.models import Favorite, Follow, ShoppingList
from recipes.utilities import get_tags

register = template.Library()

RECIPES = ["рецепт", "рецепта", "рецептов"]


@register.filter()
def add_classes(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter()
def get_filter_values(request, tag):
    new_request = request.GET.copy()
    if not request.GET.getlist("filters"):
        tags_list = get_tags()
    else:
        tags_list = new_request.getlist("filters")
    if tag in tags_list:
        tags_list.remove(tag)
        new_request.setlist("filters", tags_list)
    else:
        new_request.appendlist("filters", tag)
    return new_request.urlencode()


@register.filter()
def url_with_get(request, number):
    query = request.GET.copy()
    query["page"] = number
    return query.urlencode()


@register.filter(name="is_favorite")
def is_favorite(request, recipe):
    return Favorite.objects.filter(user=request.user, recipe=recipe).exists()


@register.filter(name="is_follower")
def is_follower(request, profile):
    return Follow.objects.filter(user=request.user, author=profile).exists()


@register.filter(name="is_in_purchases")
def is_in_purchases(request, recipe):
    return ShoppingList.objects.filter(
        user=request.user, recipe=recipe
    ).exists()


@register.filter
def declination(num):
    num -= 3
    if (num % 10 == 1) and (num % 100 != 11):
        word_out = RECIPES[0]
    elif (
        (num % 10 >= 2)
        and (num % 10 <= 4)
        and (num % 100 < 10 or num % 100 >= 20)
    ):
        word_out = RECIPES[1]
    else:
        word_out = RECIPES[2]
    return word_out
