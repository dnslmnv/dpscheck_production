from django.urls import path, include
from . import views
from django.urls import path
from .views import add_marker, get_markers
urlpatterns = [
    path('', views.index, name='index'),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('add_marker/', add_marker, name='add_marker'),
    path('get_markers/', get_markers, name='get_markers'),
]
