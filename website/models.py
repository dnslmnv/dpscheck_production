from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class Marker(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def is_active(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=59)