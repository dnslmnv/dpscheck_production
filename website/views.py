from django.shortcuts import render
import telebot
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
import json

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


def index(request):
    return render(request, 'index.html')
def home(request):
    return render(request, 'home.html')    
    
def login(request): 
    return render(request, 'login.html')

def telegram_auth(request):
    tg_user = request.GET.get('tg_user')
    if tg_user:
        tg_user_data = json.loads(tg_user)
        username = tg_user_data['username']
        first_name = tg_user_data['first_name']
        last_name = tg_user_data['last_name']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name)
            user.set_unusable_password()
            user.save()

        user = authenticate(username=username)
        if user:
            login(request, user)

        return redirect('index')
    return redirect('login')