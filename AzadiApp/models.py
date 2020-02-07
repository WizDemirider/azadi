from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.

coordinates_scale = 1000000

ATTACK_CHOICES = (
    ('p', "physical attack"),
    ('f', "fall detected"),
    ('h', "heart attack"),
    ('o', "Outside Range"),
)

class AppUser(AbstractUser):
    phone = models.CharField(max_length=13, null=True)

class Watch(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    owner = models.ForeignKey(AppUser, related_name='watch', on_delete=models.CASCADE)
    last_location = models.CharField(max_length=250, null=True, default=None)
    full_location = models.TextField(null=True, default=None)
    type_of_attack = models.CharField(max_length=2, choices=ATTACK_CHOICES, null=True)
    trusted_users = models.ManyToManyField(AppUser, related_name='watches')
    home_latitude = models.BigIntegerField(null=True)
    home_longitude = models.BigIntegerField(null=True)
    track_location = models.BooleanField(default=False)

    def get_home_coordinates(self):
        if self.home_latitude and self.home_longitude:
            return self.home_latitude/coordinates_scale, self.home_longitude/coordinates_scale
        else:
            return None

    def set_home_coordinates(self, x, y):
        self.home_latitude = x*coordinates_scale
        self.home_longitude = y*coordinates_scale

class History(models.Model):
    watch = models.ForeignKey(Watch, related_name='history', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.BigIntegerField(null=True)
    longitude = models.BigIntegerField(null=True)
    heartrate = models.IntegerField(null=True)
    location_requested = models.BooleanField(default=False)

    def get_coordinates(self):
        if self.latitude and self.longitude:
            return self.latitude/coordinates_scale, self.longitude/coordinates_scale
        else:
            return None

    def set_coordinates(self, x, y):
        self.latitude = x*coordinates_scale
        self.longitude = y*coordinates_scale