from django.shortcuts import render, redirect, HttpResponseRedirect
import pyrebase
from . import config
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import date
from django.views.decorators.cache import never_cache
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import json


firebase = pyrebase.initialize_app(config.myConfig())

auth_fb = firebase.auth()
db = firebase.database()

@csrf_exempt
def home(request):
    return render(request, 'home.html')
    
@csrf_exempt
def login(request):
    return render(request, 'login.html')


@csrf_exempt
def _login_(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        password = request.GET.get('pass')
        try:
            user = auth_fb.sign_in_with_email_and_password(email, password)
            name = ''
            if user is not None:
                uid = user["localId"]
                user_details = dict(db.child("users").child(uid).get().val())
                request.session['token_id'] = user['idToken']
                request.session['uid'] = str(user['localId'])
                #name = user_info['name']
            #user = auth.refresh(user['refreshToken'])
        except Exception as e:
            # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            msg = error['message']
            return render(request, "login.html", {"data": msg})
    try:        
        if request.session['token_id'] is not None:
            return render(request, "home.html", {"data": user_details}) 
    except KeyError:
        return render(request, "login.html", {"data": "You're logged out"})

@csrf_exempt
def register(request):
    return render(request, 'register.html')

@csrf_exempt
def _register_(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        name = request.POST.get('name')
        try:
            user = auth_fb.create_user_with_email_and_password(email, password)
            user['displayName'] = name
            uid = user['localId']
            email = user['email']
            index_of_at = email.find("@")
            username = email[:index_of_at]
            today = date.today()
            joined = today.strftime("%B %d, %y")
            
            userData = {
                'name': name,
                'email': email,
                'joined': joined,
                'userID': uid,
                'username': username,
                'image' : 'https://react.semantic-ui.com/images/wireframe/square-image.png'
            }
            db.child('users').child(uid).set(userData);
        except Exception as e:
        # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            msg = error['message']
            return render(request, "register.html", {"data": msg})

    return render(request, "login.html")

@csrf_exempt
def profile(request):
    try:        
        if request.session['uid'] is not None:
            uid = request.session['uid']
            user = db.child("users").child(uid).get().val()
            user_details = dict(user)
            print(user_details)

            return render(request, "profile.html", {"data" : user_details})
    except KeyError:
        return render(request, "login.html", {"data": "You are not logged in"})
    

@csrf_exempt
def _profile_(request):
    return render(request, "settings")

@csrf_exempt
def _logout_(request):
    try:
        auth.logout(request)
        del request.session['token_id']
    except KeyError:
        pass    
    return render(request, "login.html")

        
