from django import forms

from .models import Recipe, Tag, User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = (
            "title",
            "ingredient",
            "description",
            "image",
            "cooking_time",
        )

    tag = forms.ModelMultipleChoiceField(
        Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )
    ingredient = forms.CharField(max_length=250, required=False)
    image = forms.ImageField(
        required=True)
    cooking_time = forms.fields.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form__input", "autocomplete": "off"}
        ),
    )
