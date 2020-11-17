
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.utils.html import escape

from .models import *

def signupUser(request):
    if request.method == 'POST':
        username = escape(request.POST.get('username'))
        email = escape(request.POST.get('email'))
        phone = escape(request.POST.get('phone'))
        raw_password = escape(request.POST.get('password1'))
        raw_password2 = escape(request.POST.get('password2'))
        try:
            if raw_password == raw_password2 and len(raw_password) >= 6:
                user = AppUser.objects.create(username=username, password=raw_password, email=email, phone=phone)
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