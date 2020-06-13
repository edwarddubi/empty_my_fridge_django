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
from cpanel.model.user import User
from validate_email import validate_email
from . import food_network
from cpanel.model.recipes import Recipes

firebase = pyrebase.initialize_app(config.myConfig())

auth_fb = firebase.auth()
db = firebase.database()
m_user = User()
recipes = Recipes()


@csrf_exempt
def home(request):
    admin = db.child("admin").child("UPLwshBH98OmbVivV").get().val()
    if admin["scrape"]:
        db.child("recipe").remove()
        food_network.food_network()
        scrape_db_population = False
        db.child("admin").child("UPLwshBH98OmbVivV").child("scrape").set(scrape_db_population)

    all_recipes = db.child("recipe").get()
    recipe_list = []
    for recipe in all_recipes.each():
        recipe_details = dict(recipe.val())
        recipe_list.append(recipe_details)

    recipes.set_all_recipes(recipe_list)    
    if m_user._isNone_():
        return render(request, 'home.html', {"recipes": recipe_list})
    else:
        user_details = m_user._getUser_()
        return render(request, 'home.html', {"data": user_details, "recipes": recipe_list})


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
            if user is not None:
                uid = user["localId"]
                _user_ = db.child("users").child(uid).get().val()
                m_user._setUser_Id_(uid)
                user_details = dict(_user_)
                m_user._setUser_(user_details)
                request.session['token_id'] = user['idToken']
                request.session['uid'] = uid
                #name = user_info['name']
            #user = auth.refresh(user['refreshToken'])
        except Exception as e:
            # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            print(error['message'])
            msg = error_message(error['message'])
            return render(request, "login.html", {"data": msg})
    try:
        if request.session['token_id'] is not None:
            return render(request, "home.html", {"data": user_details, "recipes": recipes.get_all_recipes()})
    except KeyError:
        return render(request, "login.html")


@csrf_exempt
def register(request):
    return render(request, 'register.html')


@csrf_exempt
def _register_(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        name = request.POST.get('name')
        #is_email_valid = validate_email(email, verify=True)
        is_email_valid = True #validate_email(email, verify=True)
        if is_email_valid:
            register_user(request, email, password, name)
        else:
            msg = error_message("WRONG_EMAIL")
            return render(request, "register.html", {"data": msg})

    return render(request, "login.html")


def register_user(request, email, password, name):
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
            'image': 'https://react.semantic-ui.com/images/wireframe/square-image.png'
        }
        db.child('users').child(uid).set(userData)
    except Exception as e:
        # logging.exception('')
        response = e.args[0].response
        error = response.json()['error']
        msg = error_message(error['message'])
        return render(request, "register.html", {"data": msg})


@csrf_exempt
def profile(request):
    if m_user._isNone_():
        return render(request, "login.html")
    else:
        uid = m_user._getUser_Id_()
        user = db.child("users").child(uid).get().val()
        user_details = dict(user)
        m_user._setUser_(user_details)
        return render(request, "profile.html", {"data": user_details})

@csrf_exempt
def edit_profile(request):
    if m_user._isNone_():
        return render(request, "login.html")  
    else:
        user_details = m_user._getUser_()
        return render(request, 'edit_profile.html', {"data": user_details})

@csrf_exempt
def save_profile(request):
    user_details = m_user._getUser_()
    uid = m_user._getUser_Id_()
    msg = error_message("err")
    msg_type = "error"
    if m_user._isNone_():
        return render(request, "login.html") 
    else:
        if request.method == "POST":
            name = request.POST.get("name")
            bio = request.POST.get("bio")
            country = request.POST.get("country")
            blog = request.POST.get("blog")
            state = request.POST.get("state")
            userData = {
                'name': name,
                'bio': bio,
                'country': country,
                'blog': blog,
                'state': state
            }
            try:
                db.child("users").child(uid).update(userData)
                _user_ = dict(db.child("users").child(uid).get().val())
                m_user._setUser_(_user_)
                user_details = _user_
                msg = "Changes saved successfully."
                msg_type = "success"
            except Exception as e:
                pass

    return render(request, 'edit_profile.html', {"data": user_details, "message": msg, "msg_type" : msg_type})

@csrf_exempt
def account_settings(request):
    if m_user._isNone_():
        return render(request, "login.html")
    else:
        user_details = m_user._getUser_()
        return render(request, 'account_settings.html', {"data": user_details})

@csrf_exempt
def recover_password(request):
    user_details = m_user._getUser_()
    uid = m_user._getUser_Id_()
    msg = error_message("err")
    msg_type = "error"
    if m_user._isNone_():
        return render(request, "login.html") 
    else:
        if request.method == "POST":
            email = request.POST.get("email")
            try:
                auth_fb.send_password_reset_email(email)
                msg = "A password recovery link has been sent to your email."
                msg_type = "success"
            except Exception as e:
                print(e)    

    return render(request, 'account_settings.html', {"data": user_details, "message": msg, "msg_type" : msg_type})



@csrf_exempt
def _profile_(request):
    return render(request, "settings")


def error_message(type):
    return {
        "EMAIL_EXISTS": "This email is already in use. Try a different email!",
        "WEAK_PASSWORD": "Password should be at least 6 characters.",
        "INVALID_EMAIL": "The email you provided is invalid.",
        "INVALID_PASSWORD": "The password you provided for this email is wrong. Click on Forgot Password to recover your account.",
        "EMAIL_NOT_FOUND": "This email does not exist anywhere on our services.",
        "WRONG_EMAIL": "Please make sure you are using a valid email address."

    }.get(type, "An unknown error has occurred")


@csrf_exempt
def _logout_(request):
    m_user._setUser_(None)
    m_user._setUser_Id_(None)
    #del m_user
    try:
        del request.session['token_id']
        del request.session["uid"]
        auth.logout(request)
    except KeyError:
        pass
    return render(request, "login.html")
