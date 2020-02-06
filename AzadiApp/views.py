from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.html import escape

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status

from datetime import datetime, timedelta
import json
import requests
from . import utils

from .models import *
from .serializers import *
import random


def index(request):
    return redirect('login')

def signupUser(request):
    if request.method == 'POST':
        username = escape(request.POST.get('username'))
        raw_password = escape(request.POST.get('password1'))
        raw_password2 = escape(request.POST.get('password2'))
        try:
            if raw_password == raw_password2 and len(raw_password) >= 6:
                user = User.objects.create(username=username, password=raw_password)
                user.set_password(raw_password)
                user.save()
                login(request, user) # logs User in
                return redirect('my-watches')
            elif len(raw_password) >= 6:
                return render(request, 'Authentication/signup.html', {'error': "Passwords do not match!"})
            else:
                return render(request, 'Authentication/signup.html', {'error': "Password must be 6 characters or more"})
        except Exception as e:
            return render(request, 'Authentication/signup.html', {'error': str(e)})
    return render(request, 'Authentication/signup.html', {'error': None})

def loginUser(request):
    if request.method == 'POST':
        username = escape(request.POST.get('username'))
        raw_password = escape(request.POST.get('password'))
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(request, user) # logs User in
            return redirect('my-watches')
        else:
            return render(request, 'Authentication/signup.html', {'error': "Unable to Log you in!"})
    return render(request, 'Authentication/login.html', {'error': None})

def logoutUser(request):
    logout(request)
    return redirect('index')

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
        watches.extend(list(request.user.watches.all()))
    return render(request, 'my_watches.html', {'success': success, 'watches': WatchSerializer(watches, many=True).data})

@login_required
def fullData(request, wid):
    watch = Watch.objects.get(id=wid)
    history = History.objects.filter(watch=watch).order_by('-timestamp')
    return render(request, 'full-data.html', {'watch': watch, 'history': history[:15], 'watch_json': WatchSerializer(watch).data});


class PostData(generics.GenericAPIView):
    # permission_classes = (AllowAny,)

    def post(self, request, token):
        try:
            watch = Watch.objects.get(id=token)
        except Watch.DoesNotExist:
            return JsonResponse({
                'error_message': "Watch not found. Check the token sent."
            }, status=status.HTTP_400_BAD_REQUEST)

        owner = watch.owner
        new_data = History(watch=watch)
        loc = "No coordinates sent."

        recv_data = request.body.decode()
        try:
            fall, clat, clong, curr_hr = [float(val) for val in recv_data.split('&')]
        except Exception:
            fall = 0.0
            clat = 19.0968
            clong = 72.8517
            curr_hr = 0.0
        print("data", recv_data)

        if clat and clong:
            new_data.set_coordinates(clat, clong)
            if History.objects.filter(watch=watch, location_requested=True).exists():
                last_req = History.objects.filter(watch=watch, location_requested=True).latest('timestamp')
                if utils.haversine(new_data.get_coordinates(), last_req.get_coordinates())['km'] > 1:
                    res = requests.get('https://api.opencagedata.com/geocode/v1/json?q='+str(clat)+'+'+str(clong)+'&key=f80b2fa819d443819a1545a667753d9f')
                    data = res.json()['results']
                    # loc = [location['formatted'] for location in data]
                    if 'county' in data[0]['components']:
                        loc = data[0]["components"]["county"]
                        watch.last_location = data[0]["components"]["county"]
                    else:
                        loc = data[0]["components"]["city"]
                        watch.last_location = data[0]["components"]["city"]
                    watch.full_location = data[0]["formatted"]
                    watch.save()
                    new_data.location_requested = True
                else:
                    loc = watch.last_location
            else:
                res = requests.get('https://api.opencagedata.com/geocode/v1/json?q='+str(clat)+'+'+str(clong)+'&key=f80b2fa819d443819a1545a667753d9f')
                data = res.json()['results']
                # loc = [location['formatted'] for location in data]
                if 'county' in data[0]['components']:
                    loc = data[0]["components"]["county"]
                    watch.last_location = data[0]["components"]["county"]
                else:
                    loc = data[0]["components"]["city"]
                    watch.last_location = data[0]["components"]["city"]
                watch.full_location = data[0]["formatted"]
                watch.save()
                new_data.location_requested = True

        if curr_hr:
            new_data.heartrate = int(curr_hr)
        else:
            new_data.heartrate = random.randint(79, 85)
        new_data.save()

        # if b_pressed == 1.0:
        #     watch.type_of_attack = None
        #     watch.save()

        if fall:
            watch.type_of_attack = 'f'
            watch.save()
            utils.send_alerts()

        if watch.type_of_attack != None:
            atk = '1'
        else:
            atk = '0'

        return HttpResponse(atk+(new_data.timestamp+timedelta(hours=5, minutes=30)).strftime('%d/%m/%y')+(new_data.timestamp+timedelta(hours=5, minutes=30)).strftime('%I:%M %p')+str(new_data.heartrate)+loc)

class AttackPressed(generics.GenericAPIView):

    def get(self, request, wid):
        watch = Watch.objects.get(id=wid)
        if watch.type_of_attack == None:
            watch.type_of_attack = 'p'
            watch.save()
            utils.send_alerts()
        else:
            watch.type_of_attack = None
            watch.save()
        return JsonResponse({})
