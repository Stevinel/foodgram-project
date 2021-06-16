from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    title = models.CharField("Название рецепта", max_length=50)
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    image = models.ImageField(
        "Фотография",
        upload_to="recipes/",
    )
    ingredient = models.ManyToManyField(
        "Ingredient",
        through="IngredientItem",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
    )
    tag = models.ManyToManyField("Tag", related_name="recipes")
    cooking_time = models.PositiveIntegerField("Время приготовления")
    description = models.TextField(null=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField("Название ингредиента", max_length=100)
    dimension = models.CharField("Единица измерения", max_length=10)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=15, db_index=True)
    value = models.CharField(max_length=20, null=True)
    color = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name="favorites_recipes",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="in_user_favorites",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"user: {self.user.username}, recipe:{self.recipe.title}"


class IngredientItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    quantity = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),)
    )

    def __str__(self):
        return self.ingredient.title


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        related_name="user_shopping_lists",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shop_list",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shoppinglist"
            )
        ]

    def __str__(self):
        return f"user: {self.user.username}, recipe:{self.recipe.title}"
        

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]

    def __str__(self):
        return (
            f"follower: {self.user.username}, following:{self.author.username}"
        )

