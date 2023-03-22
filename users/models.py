from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from tokens.models import Event

# Create your models here.
class User(AbstractUser):
    phone = models.CharField(_("Phone"),unique=True,blank=True,null=True,max_length=15)
    name = models.CharField(max_length=50,null=True,blank=True)
    is_admin = models.BooleanField(default=False)
    is_executive = models.BooleanField(default=True)


class EventPermission(models.Model):
    event = models.ForeignKey(Event,verbose_name=("Event"),null=True,blank=True,on_delete=models.CASCADE)
    user = models.ForeignKey(User,verbose_name=("User"),null=True,blank=True,on_delete=models.CASCADE) 

    def __str__(self):
        return f'{self.user} - {self.event}'