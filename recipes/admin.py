from django.contrib import admin

from .models import Follow, Ingredient, IngredientItem, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = IngredientItem
    fields = ["ingredient", "quantity"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "title", "image", "cooking_time")
    search_fields = ("title",)
    empty_value_display = "-пусто-"
    inlines = [IngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "dimension")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    empty_value_display = "-пусто-"


@admin.register(IngredientItem)
class IngredientItemAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "recipe",
        "ingredient",
        "quantity",
    )
    list_display_links = ("pk", "recipe")
    list_filter = (
        "recipe",
        "ingredient",
    )
