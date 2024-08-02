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