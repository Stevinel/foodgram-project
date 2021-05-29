from django.contrib import admin

from .models import Recipe, Ingredient, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "title", "image", "cooking_time", "slug")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "quantity", "measure")
    empty_value_display = "-пусто-"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    empty_value_display = "-пусто-"
