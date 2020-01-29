from rest_framework import serializers
from .models import *


class WatchSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField('get_location')


    class Meta:
        model = Watch
        fields = ('id', 'owner', 'location')

    def get_location(self, watch):
        try:
            last_req = History.objects.filter(watch=watch).latest('timestamp')
            GeoJson = {
                "type": "FeatureCollection",
                "features": []
            }
            data = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": list(last_req.get_coordinates()).append(0)
                }
            }
            GeoJson['features'].append(data)

        except Exception as e:
            print(e)
            GeoJson = None
        return GeoJson