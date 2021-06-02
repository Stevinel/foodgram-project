from django.db import models
from users.models import User
from django.core.exceptions import ValidationError



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
    ingredients = models.ManyToManyField("Ingredient")
    tag = models.ManyToManyField("Tag")
    cooking_time = models.PositiveIntegerField("Время приготовления в минутах", validators=[validate_not_zero])
    description = models.TextField(null=True)
    slug = models.SlugField("Адрес",
        max_length=256,
        unique=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField("Название ингредиента",max_length=50)
    quantity = models.PositiveIntegerField("Количество")
    measure = models.CharField("Единица измерения",max_length=10)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title

class Tag(models.Model):
    title = models.CharField("Тэг", max_length=15)
    
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
        