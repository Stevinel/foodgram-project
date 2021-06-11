from django.urls import path, include

from recipes import views


urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('profile/<username>/', views.profile, name='profile'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('follow/', views.follow_index, name='follow'),
    path("shop_list/", views.shop_list, name="shop_list"),
    path('ingredients/', views.ingredients, name='ingredients'),
    path('recipe_edit/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
    path(
        "<str:username>/<int:recipe_id>/delete",
        views.recipe_delete,
        name="recipe_delete"
    ),
    path("favorites/", views.favorites, name="favorites"),
    path(
        "change_favorites/<int:recipe_id>",
        views.change_favorites,
        name="change_favorites"
    ),
    path("purchases", views.get_purchases, name="get_purchases"),
    path("purchases/<int:recipe_id>", views.purchases, name="purchases"),
    path(
        "subscriptions/<int:author_id>",
        views.subscriptions,
        name="subscriptions"
    ),
    path(
        "<str:username>/profile_edit", views.profile_edit, name="profile_edit"
    ),
]