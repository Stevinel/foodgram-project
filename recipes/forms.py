from django import forms
from django.forms.fields import CharField

from .models import Ingredient, Recipe, Tag, User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class RecipeCreateForm(forms.ModelForm):
    tag = forms.ModelMultipleChoiceField(
        Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={"required": "Выберите тег"},
    )
    image = forms.ImageField(
        required=True, error_messages={"required": "Не выбрано фото"}
    )
    cooking_time = forms.fields.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form__input", "autocomplete": "off"}
        ),
    )

    class Meta:
        model = Recipe
        fields = ["title", "tag", "image", "description", "cooking_time"]
        widgets = {"tag": forms.CheckboxSelectMultiple()}
