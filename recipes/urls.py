from django.urls import path, include

from recipes import views


urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<slug:slug>/', views.recipe_view, name='recipe'),
    path('profile/<username>/', views.profile, name='profile'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('follow/', views.follow_index, name='follow'),
    path("shop_list/", views.shop_list, name="shop_list"),
    path('ingredients/', views.ingredients, name='ingredients'),
    path('recipe_edit/<slug:slug>/', views.recipe_edit, name='recipe_edit'),
    path("favorites/", views.favorites, name="favorites"),
    path(
        "change_favorites/<int:recipe_id>",
        views.change_favorites,
        name="change_favorites"
    ),
    path('subscriptions/', views.subscription, name='subscription'),
    path('subscriptions/<int:author_id>', views.delete_subscription,
         name='delete_subscription'),
]