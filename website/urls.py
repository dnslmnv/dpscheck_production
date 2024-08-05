from django.urls import path, include
from . import views
from django.urls import path
from .views import add_marker, get_markers
urlpatterns = [
    path('', views.index, name='index'),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('home/', views.home, name='home'),
    path('add_marker/', add_marker, name='add_marker'),
    path('get_markers/', get_markers, name='get_markers'),
    path('extend_marker/<int:id>/', views.extend_marker, name='extend_marker'),
    path('delete_marker/<int:id>/', views.delete_marker, name='delete_marker'),
    path('can_add_marker/', views.marker_can_add, name='can_add_marker'),
    path('profile/', views.user_profile, name='profile'),
]
