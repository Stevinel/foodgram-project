from django import forms

from .models import Recipe, User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "tag", "image", "description", "cooking_time"]
        widgets = {"tag": forms.CheckboxSelectMultiple()}
