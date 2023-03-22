from django.contrib import admin
from .models import Token, Event, StudentList
# Register your models here.

admin.site.register(Token)
admin.site.register(Event)
# admin.site.register(Tag)
admin.site.register(StudentList)

