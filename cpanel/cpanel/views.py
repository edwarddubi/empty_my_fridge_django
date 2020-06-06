from django.shortcuts import render, redirect, HttpResponseRedirect
import pyrebase
from . import config
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


firebase = pyrebase.initialize_app(config.myConfig())

auth = firebase.auth()
db = firebase.database()


@csrf_exempt
def sign_in(request):
    return render(request, 'signIn.html')


@csrf_exempt
def _sign_in_(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            #user = auth.refresh(user['refreshToken'])
        except Exception as e:
            # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            msg = error['message']
            return render(request, "signIn.html", {"data": msg})

    return render(request, "home.html", {"data": user})
        
