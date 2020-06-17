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
import dns
from validate_email import validate_email
from . import food_network
from cpanel.model.recipes import Recipes
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

firebase = pyrebase.initialize_app(config.myConfig())

auth_fb = firebase.auth()
db = firebase.database()
m_user = User()
recipes = Recipes()

##Home Page
@csrf_exempt
def home(request):   
    if m_user._isNone_():
        return render(request, 'home.html')
    else:
        user_details = m_user._getUser_()
        return render(request, 'home.html', {"data": user_details})

##get all recipes
def get_all_recipes():
    admin = db.child("admin").child("UPLwshBH98OmbVivV").get().val()
    if admin != None:
        if admin["scrape"]:
            db.child('all_ingredients').remove()
            food_network.food_network(db)
            scrape_and_populate_db = False
            db.child("admin").child("UPLwshBH98OmbVivV").child("scrape").set(scrape_and_populate_db)
    else:
        scrape = {
            "scrape" : False,
        }
        db.child("admin").child("UPLwshBH98OmbVivV").set(scrape)
    
    all_recipes = db.child("recipe").get()
    
    recipe_list = []
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            key = recipe.key()
            recipe_details = dict(recipe.val())
            _key_ = str(key)
            _stars_ = 0
            fav = False
            no_user_signed_in = True
            num_of_stars = db.child("recipe").child(_key_).child("stars").get().val()
            if num_of_stars != None:
                _stars_ = len(num_of_stars.items())
            if not m_user._isNone_():
                no_user_signed_in = False
                uid = m_user._getUser_Id_()
                fav = db.child("recipe").child(_key_).child("stars").child(uid).get().val() != None
            recipe_details["recipe_id"] = _key_
            recipe_details["user_saved"] = fav
            recipe_details["likes"] = _stars_
            recipe_details["no_user_signed_in"] = no_user_signed_in

            recipe_list.append(recipe_details)

    recipes.set_all_recipes(recipe_list)
    return recipe_list

##get all filtered recipes
def get_all_filtered_recipes():
    recipe_list = []
    word = 'chick'
    if recipes.get_word_to_filter():
        word = recipes.get_word_to_filter().lower()
    all_recipes = db.child("recipe").get()
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            recipe_name = recipe.val()["recipe_name"]
            if recipe_name.lower().find(word) != -1:
                key = recipe.key()
                recipe_details = dict(recipe.val())
                _key_ = str(key)
                _stars_ = 0
                fav = False
                no_user_signed_in = True
                num_of_stars = db.child("recipe").child(_key_).child("stars").get().val()
                if num_of_stars != None:
                    _stars_ = len(num_of_stars.items())
                if not m_user._isNone_():
                    no_user_signed_in = False
                    uid = m_user._getUser_Id_()
                    fav = db.child("recipe").child(_key_).child("stars").child(uid).get().val() != None
                recipe_details["recipe_id"] = _key_
                recipe_details["user_saved"] = fav
                recipe_details["likes"] = _stars_
                recipe_details["no_user_signed_in"] = no_user_signed_in

                recipe_list.append(recipe_details)

    recipes.set_all_recipes(recipe_list)
    return recipe_list

##Recipe Page
@csrf_exempt
def recipe_page(request):
    recipes.set_is_searched_for_recipes(False)
    recipes.set_word_to_filter(None)
    return HttpResponseRedirect("/recipe_list/")

@csrf_exempt
def recipe_list(request):
    found_results = False
    isSearch = False
    if recipes.get_is_searched_for_recipes():
        all_recipes = get_all_filtered_recipes()
        isSearch = True
        recipes.set_is_searched_for_recipes(False)
        if len(all_recipes) == 0:
            all_recipes = get_all_recipes()
        else:
            found_results = True    

    else:
        all_recipes = get_all_recipes()
    scrollTop = 0
    keep_scroll_pos = False
    if recipes.get_is_recipe_liked():
        scrollTop = recipes.get_recipe_list_position()
        recipes.set_is_recipe_liked(False)
        keep_scroll_pos = True
    
    paginator = Paginator(all_recipes, 8)
    page = request.GET.get('page')

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)

    if m_user._isNone_():
        return render(request, 'recipes.html', {"recipes": curr_recipes, "scrollTop" : scrollTop, "found_results" : found_results, "items" : len(curr_recipes), "isSearch": isSearch})
    else:
        user_details = m_user._getUser_()
        return render(request, 'recipes.html', {"data": user_details, "recipes": curr_recipes, "scrollTop" : scrollTop, "keep_scroll_pos" : keep_scroll_pos, "found_results" : found_results, "items" : len(curr_recipes), "isSearch": isSearch})    

##Search Page
@csrf_exempt
def search(request):
    if request.method == "POST":
        recipe_to_filter = request.POST.get("recipe_to_filter")
        recipes.set_word_to_filter(recipe_to_filter)
        recipes.set_is_searched_for_recipes(True)
    return HttpResponseRedirect("/recipe_list/")


##Actions (Recipe onClick)
@csrf_exempt
def fav_recipe_onClick(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/") 
    else:
        if request.method == "POST":
            uid = m_user._getUser_Id_()
            recipe_id = request.POST.get("recipe_id")
            navigate = request.POST.get("navigate")
            scrollTop = request.POST.get("scroll_y")
            isSearch = request.POST.get("isSearch")
            if isSearch == "True":
                recipes.set_is_searched_for_recipes(True)
            recipes.set_recipe_list_position(scrollTop)
            recipes.set_is_recipe_liked(True)
            today = date.today()
            time_now = time.time()
            time_liked = {
                "time": time_now,
            }
            _recipe_data_ = db.child("user_fav_recipes").child(uid).child(recipe_id).get().val()
            if _recipe_data_ != None:
                db.child("user_fav_recipes").child(uid).child(recipe_id).remove()
                db.child("recipe").child(recipe_id).child("stars").child(uid).remove()
            else:
                db.child("user_fav_recipes").child(uid).child(recipe_id).set(time_liked)
                db.child("recipe").child(recipe_id).child("stars").child(uid).set(time_liked)
            
            return HttpResponseRedirect(navigate)

##Authentication (Login and Register)
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
            if user != None:
                uid = user["localId"]
                _user_ = db.child("users").child(uid).get().val()
                m_user._setUser_Id_(uid)
                user_details = dict(_user_)
                m_user._setUser_(user_details)
                request.session['token_id'] = user['idToken']
                request.session['uid'] = uid
                recipe_list = get_all_recipes()
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
        return HttpResponseRedirect("/login/")


@csrf_exempt
def register(request):
    return render(request, 'register.html') 


@csrf_exempt
def _register_(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        name = request.POST.get('name')
        is_email_valid = validate_email(email_address=email, check_regex=True, check_mx=True, from_address='my@from.addr.ess', helo_host='my.host.name', smtp_timeout=10, dns_timeout=10, use_blacklist=True, debug=True)
        #is_email_valid = validate_email(email, verify=True)
        #is_email_valid = True #validate_email(email, verify=True)
        if is_email_valid:
            register_user(request, email, password, name)
        else:
            msg = error_message("WRONG_EMAIL")
            return render(request, "register.html", {"data": msg})

    return HttpResponseRedirect("/login/")


def register_user(request, email, password, name):
    try:
        user = auth_fb.create_user_with_email_and_password(email, password)
        user['displayName'] = name
        uid = user['localId']
        email = user['email']
        index_of_at = email.find("@")
        username = email[:index_of_at]
        today = date.today()
        joined = today.strftime("%B %d, %Y")

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

##Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)
@csrf_exempt
def profile(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/") 
    else:
        uid = m_user._getUser_Id_()
        user = db.child("users").child(uid).get().val()
        user_details = dict(user)
        m_user._setUser_(user_details)
        return render(request, "profile.html", {"data": user_details})

@csrf_exempt
def edit_profile(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/")   
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
        return HttpResponseRedirect("/login/") 
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
        return HttpResponseRedirect("/login/")
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
        return HttpResponseRedirect("/login/") 
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
def user_fav_recipes(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/")  
    else:
        user_details = m_user._getUser_()
        uid = m_user._getUser_Id_()
        fav_recipes_list = []
        fav_recipes = db.child("user_fav_recipes").child(uid).get()
        num_of_fav_recipes = 0
        if fav_recipes.each() != None:
            for recipe in fav_recipes.each():
                _key_ = str(recipe.key())
                user_fav_recipe = db.child("recipe").child(_key_).get().val()
                recipe_details = dict(user_fav_recipe)
                recipe_details["user_saved"] = True
                recipe_details["recipe_id"] = _key_
                fav_recipes_list.append(recipe_details)

        num_of_fav_recipes = len(fav_recipes_list)

        return render(request, 'user_fav_recipes.html', {"data": user_details, "fav_recipes" : fav_recipes_list, "num_of_fav_recipes" : num_of_fav_recipes})

##User Error Messages Display
def error_message(type):
    return {
        "EMAIL_EXISTS": "This email is already in use. Try a different email!",
        "WEAK_PASSWORD": "Password should be at least 6 characters.",
        "INVALID_EMAIL": "The email you provided is invalid.",
        "INVALID_PASSWORD": "The password you provided for this email is wrong. Click on Forgot Password to recover your account.",
        "EMAIL_NOT_FOUND": "This email does not exist anywhere on our services.",
        "WRONG_EMAIL": "Please make sure you are using a valid email address."

    }.get(type, "An unknown error has occurred")


##logOut
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
    return HttpResponseRedirect("/login/")
