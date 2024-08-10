from django.shortcuts import render
import telebot
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
import json
from cryptography.fernet import Fernet

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

from django.http import JsonResponse
from .models import Marker,UserProfile, LeaveAction

# def create_profiles_for_existing_users():
#     users_without_profiles = User.objects.filter(userprofile__isnull=True)
#     for user in users_without_profiles:
#         UserProfile.objects.create(user=user)

# create_profiles_for_existing_users()

def user_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Вы не аутентифицированы'}, status=403)

    # Get the current user
    user = request.user

    # Count active markers placed by the user
    active_markers_count = Marker.objects.filter(user=user).count()

    # Prepare the data to be sent in the response
    data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'active_markers_count': active_markers_count,
        'status': 'success',
    }
    print(data)
    # Return the data as a JSON response
    return JsonResponse(data, status=200)

def marker_can_add(request):
    if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Вы не аутентифицированы'}, status=403)
            
    user_profile = request.user.userprofile

        # Проверяем, можно ли добавить метку
    if not user_profile.can_add_marker():
        remaining_time = (user_profile.last_marker_time + timezone.timedelta(seconds=300)) - timezone.now()
        minutes, seconds = divmod(remaining_time.total_seconds(), 60)
        print(minutes, seconds)
        minuts_str = ''
        if minutes > 1:
            minutes_str = 'минуты'
        elif minutes == 1:
            minutes_str = 'минута'
        else:
            minutes_str = 'минут'
        return JsonResponse({
                'status': 'error',
                'message': f'Подождите<br> {int(minutes)} {minutes_str} и {int(seconds)} секунд<br> перед добавлением новой метки.'
            }, status=403)
    return JsonResponse({
                'status': 'success',
                'message': f'ok'
            }, status=200)
     
def add_marker(request):
    if request.method == "GET":
        # Убедитесь, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Вы не аутентифицированы'}, status=403)

        # Получаем профиль пользователя
        user_profile = request.user.userprofile

        # Проверяем, можно ли добавить метку
        if not user_profile.can_add_marker():
            remaining_time = (user_profile.last_marker_time + timezone.timedelta(minutes=5)) - timezone.now()
            minutes, seconds = divmod(remaining_time.total_seconds(), 60)
            return JsonResponse({
                'status': 'error',
                'message': f'Подождите {int(minutes)} минут и {int(seconds)} секунд перед добавлением новой метки.'
            }, status=403)
        
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lon')
        comment = request.GET.get('comment', '')

        # Создаем новую метку
        Marker.objects.create(
            latitude=float(latitude),
            longitude=float(longitude),
            comments=str(comment),
            user=request.user
        )

        # Обновляем время последней метки
        user_profile.last_marker_time = timezone.now()
        user_profile.marker_count += 1 
        user_profile.save()

        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()

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
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Вы не аутентифицированы'}, status=403)

    if request.user.is_superuser:
        try:
            marker = Marker.objects.get(pk=id)
            marker.delete()  # Superusers can delete immediately
            return JsonResponse({'status': 'success', 'deleted': True})
        except Marker.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Метка не найдена'}, status=404)
    try:
        marker = Marker.objects.get(pk=id)

        # Проверяем, нажимал ли пользователь на кнопку "Уехали"
        if LeaveAction.objects.filter(user=request.user, marker=marker).exists():
            print('User already left marker')
            return JsonResponse({'status': 'success', 'deleted': False, 'message': 'Вы уже отмечали метку как "Уехали"'})

        # Добавляем запись о нажатии на кнопку "Уехали"
        LeaveAction.objects.create(user=request.user, marker=marker)

        # Обновляем счётчик и проверяем, нужно ли удалять метку
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
        return JsonResponse({'status': 'error', 'message': 'Метка не найдена'}, status=404)
    
    
def index(request):
    return render(request, 'index.html')
def home(request):
    # Query the top 5 users with the most markers
    top_users = UserProfile.objects.order_by('-marker_count')[:5]

    # Pass the top users to the template context
    context = {
        'top_users': top_users
    }

    return render(request, 'home.html', context)
    
def telegram_auth(request):
    tg_user = request.GET.get('tg_user')
    if tg_user:
        tg_user_data = json.loads(tg_user)
        username = str(tg_user_data['id'])
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

key = Fernet.generate_key()
print(key)
key = b'AvbQDh6i2LIRU-Wym_QrsKjFo1vdB-qSvsqVEiA_g5w='
cipher_suite = Fernet(key)

@csrf_exempt
def get_encrypted_user_ids(request):
    # Retrieve all user IDs from UserProfile
    # user_ids = list(UserProfile.objects.values_list('user_id', flat=True))
    user_ids = [358216042]
    # Convert the list to JSON string and encrypt it
    user_ids_json = json.dumps(user_ids)
    encrypted_data = cipher_suite.encrypt(user_ids_json.encode('utf-8'))

    # Return as JSON response
    return JsonResponse({'data': encrypted_data.decode('utf-8')})