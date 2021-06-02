from django import forms

from .models import Recipe
from django.db.models.fields import CharField, SlugField
from django.forms import ModelForm, Select, Textarea
from django.forms.widgets import ClearableFileInput, TextInput


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'description', 'image', 'tag', 'cooking_time',)
        widgets = {
            "title": Textarea(
                attrs={
                    "placeholder": "Название рецепта",
                    "class": "form-control",
                }
            ),
            "tag": Select(
                attrs={
                    "placeholder": "Выберете тег",
                    "class": "form-control",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Способ приготовления",
                    "class": "form-control",
                }
            ),
            "cooking_time": Textarea(
                attrs={
                    "placeholder": "Время приготовления",
                    "class": "form-control",
                }
            ),
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            
        }