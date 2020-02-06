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

def send_alerts():
    mail = EmailMessage('Fall Alert', 'The concerned person maybe suffering from some problem contact and reach immediately', 'ankanarn@gmail.com', ['argankit@gmail.com'])
    # mail.send()
    try:
        client = Client('ACc56a907ed6141647a64a97541c6bb927', '47282bcfa151539b884f14673dfe31a6')
        message = client.messages.create(to='+918779677344', from_='+16572543063', body='The concerned person maybe suffering from some problem contact and reach immediately')
        for attr in dir(message):
            print("message.%s = %r" % (attr, getattr(message, attr)))
    except BadHeaderError:
        return False
    return True