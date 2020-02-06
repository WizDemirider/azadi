from rest_framework import serializers
from .models import *


class WatchSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField('get_location')
    owner = serializers.SerializerMethodField('get_owner')
    under_attack = serializers.SerializerMethodField('get_attack_status')

    class Meta:
        model = Watch
        fields = ('id', 'owner', 'coordinates', 'type_of_attack', 'under_attack', 'get_type_of_attack_display')

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

    def get_attack_status(self, watch):
        if watch.type_of_attack == None:
            return False
        else:
            return True