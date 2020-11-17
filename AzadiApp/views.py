from AzadiApp.utils import writelog
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.html import escape

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, StdDev

from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status

from datetime import timedelta
from . import utils

import os
from .models import *
from .serializers import *
#from . import nlp


def index(request):
    if request.user.is_authenticated:
        return redirect('my-watches')
    else:
        return redirect('login')

@login_required
def my_watches(request):
    if request.method == 'POST':
        wid = escape(request.POST.get('id'))
        Watch.objects.create(id=wid, owner=request.user)
        success = True
    else:
        success = False
    watches = list(Watch.objects.filter(owner=request.user))
    if request.user.watches.all().exists():
        # trusted users should also be able to see
        watches.extend(list(request.user.watches.all()))
    return render(request, 'my_watches.html', {'success': success, 'watches': WatchSerializer(watches, many=True).data})

@login_required
def fullData(request, wid):
    watch = Watch.objects.get(id=wid)
    history = History.objects.filter(watch=watch).order_by('-timestamp')
    return render(request, 'full-data.html', {'watch': watch, 'history': history[:15], 'watch_json': WatchSerializer(watch).data, 'heartrates': [h.heartrate for h in history[:15]], 'timestamps': [(h.timestamp+timedelta(hours=5, minutes=30)).strftime('%I:%M:%S') for h in history[:15:-1]]});


class PostData(generics.GenericAPIView):
    # permission_classes = (AllowAny,)

    def analyze_heartrate(watch, current_hr):
        history = History.objects.filter(watch=watch)
        mean = history.aggregate(Avg('heartrate'))
        stddev = history.aggregate(StdDev('heartrate'))
        if stddev < abs(current_hr - mean):
            watch.type_of_attack = 'h'
            watch.save()
            utils.send_alerts(watch.id)

    def post(self, request, wid):
        try:
            watch = Watch.objects.get(id=wid)
        except Watch.DoesNotExist:
            return HttpResponse("Watch not found. Check the token sent.", status=status.HTTP_400_BAD_REQUEST)

        new_data = History(watch=watch)
        loc = "No coordinates sent."

        recv_data = request.body.decode()
        try:
            clat, clong, curr_hr, b_pressed, fall = [float(val) for val in recv_data.split('&')]
        except Exception:
            return HttpResponse("Data format is wrong, expected lat, long, hr, button_pressed and fall_detected.", status=status.HTTP_400_BAD_REQUEST)
        if os.environ['DEBUG']:
            writelog("data", recv_data)

        if clat and clong:
            new_data.set_coordinates(clat, clong)

            if watch.track_location and watch.type_of_attack != 'o' and watch.get_home_coordinates() and utils.haversine(new_data.get_coordinates(), watch.get_home_coordinates())['km'] > 1:
                watch.type_of_attack = 'o'
                watch.save()
                utils.send_alerts(watch)
            elif watch.type_of_attack == 'o':
                watch.type_of_attack = None
                watch.save()

            recent_history = History.objects.filter(watch=watch, location_requested=True)
            if recent_history.exists():
                last_req = recent_history.latest('timestamp')
                if utils.haversine(new_data.get_coordinates(), last_req.get_coordinates())['km'] > 1:
                    watch.last_location, watch.full_location = utils.get_location_from_coords(clat, clong)
                    watch.save()
                    new_data.location_requested = True
            else:
                watch.last_location, watch.full_location = utils.get_location_from_coords(clat, clong)
                watch.save()
                new_data.location_requested = True

            loc = watch.last_location

        if curr_hr:
            new_data.heartrate = int(curr_hr)
            # analyse heartrate
            self.analyze_heartrate(watch, int(curr_hr))
        else:
            new_data.heartrate = None
        new_data.save()

        if fall == 1.0:
            watch.type_of_attack = 'f'
            watch.save()
            utils.send_alerts(watch.id)

        if b_pressed == 1.0:
            watch.type_of_attack = None
            watch.save()

        if watch.type_of_attack != None:
            atk = '1'
        else:
            atk = '0'

        # writelog(nlp.detect_problem())
        timestamp = new_data.timestamp+timedelta(hours=5, minutes=30)

        return HttpResponse(atk+timestamp.strftime('%d/%m/%y')+timestamp.strftime('%I:%M %p')+str(new_data.heartrate)+loc+recv_data)

class AttackPressed(generics.GenericAPIView):

    def get(self, request, wid):
        watch = Watch.objects.get(id=wid)
        if watch.type_of_attack == None:
            watch.type_of_attack = 'p'
            watch.save()
            utils.send_alerts(watch.id)
            writelog("Physical Attack")
        else:
            watch.type_of_attack = None
            watch.save()
        return JsonResponse({})

class TrackLocationToggle(generics.GenericAPIView):

    def get(self, request, wid):
        watch = Watch.objects.get(id=wid)
        watch.track_location = not watch.track_location
        watch.save()
        return JsonResponse({})

# class FallDetected(generics.GenericAPIView):

#     def post(self, request, wid):
#         try:
#             watch = Watch.objects.get(id=wid)
#         except Watch.DoesNotExist:
#             return HttpResponse("Watch not found. Check the token sent.", status=status.HTTP_400_BAD_REQUEST)

#         fall = int(request.body.decode())
#         if fall:
#             watch.type_of_attack = 'f'
#             watch.save()
#             writelog("Fall Detected")
#             utils.send_alerts(watch.id)

#         return HttpResponse(str(fall))