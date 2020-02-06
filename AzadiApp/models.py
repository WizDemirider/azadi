from django.db import models
from django.contrib.auth.models import User

# Create your models here.

coordinates_scale = 1000000
ATTACK_CHOICES = (
    ('p', "physical attack"),
    ('f', "fall"),
    ('h', "heart attack"),
)

class Watch(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    owner = models.ForeignKey(User, related_name='watch', on_delete=models.CASCADE)
    last_location = models.CharField(max_length=250, null=True, default=None)
    full_location = models.TextField(null=True, default=None)
    under_attack = models.BooleanField(default=False)
    type_of_attack = models.CharField(max_length=2, choices=ATTACK_CHOICES, null=True)
    trusted_users = models.ManyToManyField(User, related_name='watches')

class History(models.Model):
    watch = models.ForeignKey(Watch, related_name='history', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.BigIntegerField(null=True)
    longitude = models.BigIntegerField(null=True)
    heartrate = models.IntegerField(null=True)
    location_requested = models.BooleanField(default=False)

    def get_coordinates(self):
        return self.latitude/coordinates_scale, self.longitude/coordinates_scale

    def set_coordinates(self, x, y):
        self.latitude = x*coordinates_scale
        self.longitude = y*coordinates_scale