from django.db import models
from django.utils import timezone

import datetime
import pytz

from hikvision.settings import MEDIA_ROOT

# Create your models here.

class deviceDetails(models.Model):
    class masterChoice(models.TextChoices):
        yes = "YES"
        no = "NO"
    class statChoice(models.TextChoices):
        Online = "Online"
        Offline = 'Offline'

    ip = models.GenericIPAddressField(null=True, blank=False, unique=True)
    port = models.IntegerField(blank=False, default=80)
    user_id = models.CharField(blank=False, max_length=10)
    password = models.CharField(blank=False, max_length=10)
    master_status = models.CharField(blank=False, choices=masterChoice.choices, default=masterChoice.no, max_length=3)
    status = models.CharField(blank=False, default=statChoice.Offline, choices=statChoice.choices, max_length=7)

    def __str__(self):
        return "{},{}".format(self.id, self.ip)

def upload_to(instance, filename):
    return f'{MEDIA_ROOT}/faces/{filename}'

class userDetails(models.Model):
    class genderChoice(models.TextChoices):
        Male = 'male'
        Female = 'female'
        Non = 'none'

    class levelChoice(models.TextChoices):
        User = 'User'
        Visitor = 'Visitor'
        Blocklist = 'Blocklist'

    IP = models.ForeignKey(deviceDetails, on_delete=models.CASCADE)
    Name = models.CharField(max_length=25, blank=True)
    gender = models.CharField(blank=True, choices=genderChoice.choices, max_length=6)
    level = models.CharField(blank=True, choices=levelChoice.choices, max_length=10, default=levelChoice.User)
    floor_number = models.IntegerField(blank=True, null=True)
    room_number = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now, editable=True)
    end_time = models.DateTimeField(default=datetime.datetime(2037, 12, 31, 23, 59, 59, tzinfo=pytz.UTC), editable=True)
    image = models.ImageField(upload_to=upload_to, blank=True)