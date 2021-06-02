from django.urls import path, include

from recipes import views


urlpatterns = [
    path('', views.index, name='index'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('profile/<username>/', views.profile, name='profile'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('follow/', views.follow_index, name='follow'),
        path(
        "subscriptions/<int:author_id>",
        views.subscriptions,
        name="subscriptions"
    ),
    path("favorites/", views.favorites, name="favorites"),
    path("shop_list/", views.shop_list, name="shop_list"),
]