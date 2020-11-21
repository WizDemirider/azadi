from datetime import date
from math import pi,sqrt,sin,cos,atan2

from django.core.mail import BadHeaderError, send_mail,EmailMessage
from twilio.rest import Client
import Azadi.settings as settings
import os, requests, datetime
from background_task import background
from .models import Watch

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

def send_mail(watch):
    try:
        mail = EmailMessage('Emergency Alert: '+watch.get_type_of_attack_display(), watch.owner.username+' may need your help! Please contact them immediately! Current Location: '+watch.full_location, 'ankanarn@gmail.com', [u.email for u in watch.trusted_users.all()])
        mail.send()
    except Exception as e:
        writelog(str(e))
        return False
    return True

def send_sms(watch):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(to=[u.phone for u in watch.trusted_users.all()], from_=os.environ['ANPHONE'], body='Emergency Alert: '+watch.get_type_of_attack_display()+'. '+watch.owner.username+' may need your help!')
        for attr in dir(message):
            writelog("message.%s = %r" % (attr, getattr(message, attr)))
    except BadHeaderError:
        return False
    except Exception as e:
        writelog(str(e))
        return False
    return True

@background(schedule=10)
def send_alerts(watch_id):
    watch = Watch.objects.get(id=watch_id)
    if watch.type_of_attack != None:
        writelog("Sending alerts about:"+watch.get_type_of_attack_display())
        return send_mail(watch) and send_sms(watch)
    else:
        return False

def get_location_from_coords(lat, long):
    try:
        url = 'https://api.opencagedata.com/geocode/v1/json?q='+str(lat)+'+'+str(long)+'&key='+os.environ['geocage_key']
        res = requests.get(url)
        data = res.json()['results']
        if 'county' in data[0]['components']:
            loc = data[0]["components"]["county"]
        else:
            loc = data[0]["components"]["city"]
    except Exception:
        raise Exception("data:"+str(res.json()))
    return loc, data[0]["formatted"]

def writelog(text, fname="debug", timestamp=True):
    with open(os.path.join(settings.BASE_DIR, fname+'.log'), 'a') as logfile:
        if timestamp:
            logfile.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")+": ")
        logfile.write(text+"\n")