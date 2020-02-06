from math import pi,sqrt,sin,cos,atan2

from django.core.mail import BadHeaderError, send_mail,EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
import urllib.request
import urllib.parse
from twilio.rest import TwilioRestClient
import time
from django.shortcuts import render
from twilio.rest import Client
from pprint import pprint
from . import my_hidden_stuff

def haversine(pos1, pos2):
    lat1 = float(pos1[0])
    long1 = float(pos1[1])
    lat2 = float(pos2[0])
    long2 = float(pos2[1])

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    km = 6367 * c
    mi = 3956 * c

    return {"km":km, "miles":mi}

def send_mail():
    try:
        mail = EmailMessage('Emergency Alert', 'The concerned person maybe suffering from some problem contact and reach immediately', 'ankanarn@gmail.com', ['argankit@gmail.com'])
        mail.send()
    except Exception as e:
        print(str(e))
        return False
    return True

def send_sms():
    try:
        client = Client(my_hidden_stuff.HKEY1, my_hidden_stuff.HKEY2)
        message = client.messages.create(to='+917506402445', from_=my_hidden_stuff.HPHONE, body='The concerned person maybe suffering from some problem contact and reach immediately')
        for attr in dir(message):
            print("message.%s = %r" % (attr, getattr(message, attr)))
    except BadHeaderError:
        return False
    except Exception as e:
        print(str(e))
        return False
    return True

def send_alerts():
    return send_mail() and send_sms()