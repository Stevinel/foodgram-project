from django.urls import path

from recipes import utilities, views

urlpatterns = [
    path("", views.index, name="index"),
    path("recipe/<int:recipe_id>/", views.recipe_view, name="recipe"),
    path("new_recipe/", views.new_recipe, name="new_recipe"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("follow/", views.follow_index, name="follow"),
    path("shop_list/", views.shop_list, name="shop_list"),
    path("favorites/", views.favorites, name="favorites"),
    path("ingredients/", utilities.ingredients, name="ingredients"),
    path("purchases/", views.download_purchases, name="download_purchases"),
    path("purchases/<int:recipe_id>/", views.purchases, name="purchases"),
    path(
        "recipe/<int:recipe_id>/edit/", views.recipe_edit, name="recipe_edit"
    ),
    path(
        "recipe/<str:username>/<int:recipe_id>/delete/",
        views.recipe_delete,
        name="recipe_delete",
    ),
    path(
        "change_favorites/<int:recipe_id>/",
        views.change_favorites,
        name="change_favorites",
    ),
    path(
        "subscriptions/<int:author_id>/",
        views.subscriptions,
        name="subscriptions",
    ),
    path("<str:username>/edit/", views.profile_edit, name="profile_edit"),
]
