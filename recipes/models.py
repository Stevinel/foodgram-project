from django.db import models
from users.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import random
import string

def random_slug(size=20, chars=string.ascii_uppercase + string.digits):
    """Generation slug code"""
    return "".join(random.choice(chars) for _ in range(size))


def validate_not_zero(value):
    if value == 0:
        raise ValidationError("Время приготовления не может быть равным нулю")

class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    title = models.CharField("Название рецепта", max_length=50)
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    image = models.ImageField("Фотография",
        upload_to="recipes/",
    )
    ingredient = models.ManyToManyField(
        'Ingredient',
        through='IngredientItem',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField("Tag")
    cooking_time = models.PositiveIntegerField("Время приготовления в минутах", validators=[validate_not_zero])
    description = models.TextField(null=True)
    slug = models.SlugField("Адрес",
        max_length=200,
        unique=True, default=random_slug
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField("Название ингредиента", max_length=50)
    dimension = models.CharField("Единица измерения", max_length=10)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингридиент',
    )
    quantity = models.PositiveSmallIntegerField(validators=(MinValueValidator(1),))

    def __str__(self):
        return self.ingredient.title

class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        related_name="shopping_list",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="in_user_shopping_list",
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
        