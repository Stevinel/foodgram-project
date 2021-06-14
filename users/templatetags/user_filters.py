from django import template

from recipes.models import Favorite, ShoppingList
from users.models import Follow

register = template.Library()


@register.filter()
def add_classes(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name="get_filter_values")
def get_filter_values(value):
    return value.getlist("filters")


@register.filter(name="get_filter_link")
def get_filter_values(request, tag):
    new_request = request.GET.copy()
    if tag.value in request.GET.getlist("filters"):
        filters = new_request.getlist("filters")
        filters.remove(tag.value)
        new_request.setlist("filters", filters)
    else:
        new_request.appendlist("filters", tag.value)
    return new_request.urlencode()


@register.filter()
def url_with_get(request, number):
    query = request.GET.copy()
    query["page"] = number
    return query.urlencode()


@register.filter(name="is_favorite")
def is_favorite(request, recipe):
    if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
        return True
    return False


@register.filter(name="is_follower")
def is_follower(request, profile):
    if Follow.objects.filter(user=request.user, author=profile).exists():
        return True
    return False


@register.filter(name="is_in_purchases")
def is_in_purchases(request, recipe):
    if ShoppingList.objects.filter(user=request.user, recipe=recipe).exists():
        return True


@register.filter
def even(num):
    if (num % 10 == 1) and (num % 100 != 11):
        word_out = "рецепт"
    elif (
        (num % 10 >= 2)
        and (num % 10 <= 4)
        and (num % 100 < 10 or num % 100 >= 20)
    ):
        word_out = "рецепта"
    else:
        word_out = "рецептов"
    return word_out
