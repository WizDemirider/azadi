from rest_framework import serializers
from .models import *


class WatchSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField('get_location')
    owner = serializers.SerializerMethodField('get_owner')

    class Meta:
        model = Watch
        fields = ('id', 'owner', 'coordinates', 'under_attack', 'type_of_attack')

    def get_location(self, watch):
        try:
            last_req = History.objects.filter(watch=watch).latest('timestamp')
            coordinates = last_req.get_coordinates()

        except Exception as e:
            print(e)
            coordinates = None
        return coordinates

    def get_owner(self, watch):
        return watch.owner.username