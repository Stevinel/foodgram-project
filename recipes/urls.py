from django.urls import path, include

from recipes import views


urlpatterns = [
    path('', views.index, name='index'),
]