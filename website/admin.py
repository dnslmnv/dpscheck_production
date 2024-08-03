from django.contrib import admin
from .models import Marker, UserProfile, LeaveAction

admin.site.register(Marker)
admin.site.register(LeaveAction)  # Новое модель LeaveAction необходим
admin.site.register(UserProfile)
# Register your models here.
