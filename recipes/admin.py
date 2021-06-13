from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "title",
        "image",
        "cooking_time",
    )
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "dimension")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    empty_value_display = "-пусто-"
