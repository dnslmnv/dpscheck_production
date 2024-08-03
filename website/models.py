from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Marker(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    leave_count = models.IntegerField(default=0)  # Новое поле для отслеживания нажатий "Уехали"
    
    def is_active(self):
        # Метка активна, если прошло меньше 59 минут и количество нажатий меньше 5
        return self.leave_count < 5 and timezone.now() < self.created_at + timezone.timedelta(minutes=59)
    

class LeaveAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user.username)+' - '+str(self.marker.id)
    
    class Meta:
        unique_together = ('user', 'marker')  # Гарантирует уникальность пары пользователь-метка
        
        
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_marker_time = models.DateTimeField(null=True, blank=True)  # Время последней метки
    def __str__(self):
        return str(self.user.username)
    def can_add_marker(self):
        # Проверяем, прошло ли 7 минут с последнего добавления метки
        if self.last_marker_time:
            return timezone.now() >= self.last_marker_time + timezone.timedelta(seconds=300)
        return True  # Разрешаем, если метки еще не ставились


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()