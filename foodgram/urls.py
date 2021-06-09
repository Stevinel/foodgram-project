from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.flatpages import views 

urlpatterns = [
    path("", include("recipes.urls")),
    path("auth/", include("users.urls")),
    path('admin/', admin.site.urls, name='admin'),
    path("auth/", include("django.contrib.auth.urls")),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about_author'), 
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about_spec'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 