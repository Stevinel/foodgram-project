from django import template

from recipes.models import ShoppingList, Favorite
from users.models import Follow

register = template.Library()


@register.filter
def addclass(field, css):
    """
    Формирование тэгов для GET запроса
    """
    return field.as_widget(attrs={"class": css})
