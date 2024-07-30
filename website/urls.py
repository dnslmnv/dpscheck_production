from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
  
]
