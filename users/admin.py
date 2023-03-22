from django.contrib import admin
from .models import User,  EventPermission
# Register your models here.
admin.site.register(User)
admin.site.register(EventPermission)