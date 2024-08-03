from django.shortcuts import render
import telebot
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
import json

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

from django.http import JsonResponse
from .models import Marker

def add_marker(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')
    comment = request.GET.get('comment', '') 
    Marker.objects.create(
            latitude=float(latitude),
            longitude=float(longitude),
            comments=str(comment),
            user=request.user
        )
    return JsonResponse({'status': 'success'})

def get_markers(request):
    # Получаем только активные метки
    active_markers = [marker for marker in Marker.objects.all() if marker.is_active()]
    # Удаляем неактивные метки
    Marker.objects.filter(id__in=[marker.id for marker in Marker.objects.all() if not marker.is_active()]).delete()
    data = {
        'markers': [
            {
                'lat': marker.latitude,
                'lon': marker.longitude,
                'id': marker.id,
                'created_at': marker.created_at,
                'username': marker.user.first_name,
                'comment': marker.comments,
                'leave_count': marker.leave_count  # Добавлено поле leave_count
            }
            for marker in active_markers
        ],
        'active_markers_count': len(active_markers)
    }
    return JsonResponse(data, safe=False)

@require_POST
def extend_marker(request, id):
    try:
        marker = Marker.objects.get(pk=id)
        marker.created_at = timezone.now()
        marker.save()
        return JsonResponse({'status': 'success'})
    except Marker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Marker not found'}, status=404)

@require_http_methods(["POST"])
def delete_marker(request, id):
    try:
        marker = Marker.objects.get(pk=id)
        if marker.is_active():
            marker.leave_count += 1
            if marker.leave_count >= 5:
                marker.delete()
                return JsonResponse({'status': 'success', 'deleted': True})
            else:
                marker.save()
                return JsonResponse({'status': 'success', 'deleted': False, 'leave_count': marker.leave_count})
        else:
            marker.delete()  # Удаляем метку, если она неактивна (время истекло)
            return JsonResponse({'status': 'success', 'deleted': True})
    except Marker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Marker not found'}, status=404)

def index(request):
    return render(request, 'index.html')
def home(request):
    return render(request, 'home.html')    
    

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
            # Реверсируем имя пользователя для использования в качестве пароля
            reversed_password = username[::-1]
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=reversed_password  # Устанавливаем пароль как реверсированное имя пользователя
            )

        # Аутентификация и вход пользователя
        user = authenticate(username=username, password=username[::-1])
        if user:
            login(request, user)

        return redirect('home')
    return redirect('index')