# Generated by Django 3.2.3 on 2021-06-26 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_ingredientitem_unique_recipe_ingredient"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="ingredientitem",
            name="unique_recipe_ingredient",
        ),
    ]
