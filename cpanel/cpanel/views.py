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
#import dns
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

# Home Page


@csrf_exempt
def home(request):
    if m_user._isNone_():
        return render(request, 'home.html')
    else:
        user = m_user._getUser_()
        data = {
            "user": user,
        }
        return render(request, 'home.html', {"data": data})

# get all recipes


def get_all_recipes():
    admin = db.child("admin").child("UPLwshBH98OmbVivV").get().val()
    if admin != None:
        if admin["scrape"]:
            db.child('all_ingredients').remove()
            food_network.food_network(db)
            scrape_and_populate_db = False
            db.child("admin").child("UPLwshBH98OmbVivV").child(
                "scrape").set(scrape_and_populate_db)
    else:
        scrape = {
            "scrape": False,
        }
        db.child("admin").child("UPLwshBH98OmbVivV").set(scrape)

    all_recipes = db.child("recipe").get()

    recipe_list = []
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            key = str(recipe.key())
            _recipe_ = get_recipe(dict(recipe.val()), key)
            recipe_list.append(_recipe_)

    recipes.set_all_recipes(recipe_list)

# get all filtered recipes


def get_all_filtered_recipes():
    recipe_list = []
    word = recipes.get_recipe_name_to_find()
    all_recipes = db.child("recipe").get()
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            if recipe.val()["recipe_name"].lower().find(word.lower()) != -1:
                key = str(recipe.key())
                _recipe_ = get_recipe(dict(recipe.val()), key)
                recipe_list.append(_recipe_)
    return recipe_list

# get individual recipe as Json


def get_recipe(recipe, key):
    num_of_stars = 0
    favorite = False
    no_user_signed_in = True
    stars = db.child("recipe").child(key).child("stars").get().val()
    if stars != None:
        num_of_stars = len(stars.items())
    if not m_user._isNone_():
        no_user_signed_in = False
        uid = m_user._getUser_Id_()
        favorite = db.child("recipe").child(key).child(
            "stars").child(uid).get().val() != None
    recipe["recipe_id"] = key
    recipe["user_saved"] = favorite
    recipe["likes"] = num_of_stars
    recipe["no_user_signed_in"] = no_user_signed_in

    return recipe

# Recipe Page


@csrf_exempt
def recipe_page(request):
    recipes.set_is_searched_for_recipes(False)
    recipes.set_recipe_name_to_find(None)
    navigate_to_recipe_page = "/recipe_list/"
    navigate_to_recipe_page += "?page=1"
    return HttpResponseRedirect(navigate_to_recipe_page)


@csrf_exempt
def recipe_list(request):
    found_results = False
    isSearch = False
    all_recipes = []
    if recipes.get_is_searched_for_recipes():
        all_recipes = get_all_filtered_recipes()
        isSearch = True
        recipes.set_is_searched_for_recipes(False)
        if len(all_recipes) != 0:
            found_results = True
    else:
        if recipes.get_all_recipes() != None:
            all_recipes = recipes.get_all_recipes()
        else:
            get_all_recipes()
            all_recipes = recipes.get_all_recipes()
    scrollTop = 0
    keep_scroll_pos = False
    if recipes.get_is_recipe_liked():
        scrollTop = recipes.get_recipe_list_position()
        recipes.set_is_recipe_liked(False)
        keep_scroll_pos = True

    paginator = Paginator(all_recipes, 48)
    page = request.GET.get('page')
    recipes.set_recipes_current_page(page)

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)

    if m_user._isNone_():
        data = {
            "recipes": curr_recipes,
            "scrollTop": scrollTop,
            "found_results": found_results,
            "items": len(curr_recipes),
            "isSearch": isSearch,

        }
        return render(request, 'recipes.html', {"data": data})
    else:
        _user_ = m_user._getUser_()
        data = {
            "user": _user_,
            "recipes": curr_recipes,
            "scrollTop": scrollTop,
            "keep_scroll_pos": keep_scroll_pos,
            "found_results": found_results,
            "items": len(curr_recipes),
            "isSearch": isSearch

        }
        return render(request, 'recipes.html', {"data": data})


@csrf_exempt
def category(request):
    cat = request.GET.get('category')
    recipe_lst = get_recipes_by_category(cat)
    paginator = Paginator(recipe_lst, 48)
    page = request.GET.get('page')

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)
    user = None

    if not m_user._isNone_():
        user = m_user._getUser_()

    data = {
        "user": user,
        "recipe_lst": curr_recipes
    }

    return render(request, 'category.html', {"data": data})


def get_recipes_by_category(category):
    all_recipes = db.child('recipe').get()
    recipe_lst = []
    for recipe in all_recipes.each():
        recipe_details = recipe.val()
        try:
            categories = recipe_details["recipe_categories"]
            if categories:
                if any(category in c for c in categories):
                    key = str(recipe.key())
                    _recipe_ = get_recipe(dict(recipe_details), key)
                    recipe_lst.append(_recipe_)
        except KeyError:
            pass
    return recipe_lst


def get_recipes_by_ingredients(ingredient):
    all_recipes = db.child('recipe').get()
    recipe_lst = []
    for recipe in all_recipes.each():
        #categories = recipe.val()["recipe_categories"]
        recipe_details = recipe.val()
        try:
            ingredients = recipe_details["recipe_ingredients"]
            if ingredients:
                if any(ingredient in i for i in ingredients):
                    key = str(recipe.key())
                    _recipe_ = get_recipe(dict(recipe_details), key)
                    recipe_lst.append(_recipe_)
        except KeyError:
            pass
    return recipe_lst


@csrf_exempt
def get_recipes_by_category_ingredients(request):
    category_list = []
    ingred_list = []
    result_list = []
    if request.method == "GET":
        value = request.GET.get("value")
        category_list = get_recipes_by_category(value)
        ingred_list = get_recipes_by_ingredients(value)
        result_list = category_list + ingred_list

    paginator = Paginator(result_list, 48)
    page = request.GET.get('page')

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)

    user = None

    if not m_user._isNone_():
        user = m_user._getUser_()

    data = {
        "user": user,
        "recipe_lst": curr_recipes
    }

    return render(request, 'category.html', {"data": data})


# Search Page
@csrf_exempt
def search(request):
    if request.method == "GET":
        recipe_name_to_find = request.GET.get("recipe_to_filter")
        if len(recipe_name_to_find) > 0:
            recipes.set_recipe_name_to_find(recipe_name_to_find)
            recipes.set_is_searched_for_recipes(True)
        navigate_to_recipe_page = "/recipe_list/"
        navigate_to_recipe_page += "?page=" + recipes.get_recipes_current_page()
    return HttpResponseRedirect(navigate_to_recipe_page)


# Actions (Recipe onClick)
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
            recipes.set_recipe_liked(recipe_id)
            today = date.today()
            time_now = time.time()
            time_liked = {
                "time": time_now,
            }
            _recipe_data_ = db.child("user_fav_recipes").child(
                uid).child(recipe_id).get().val()
            if _recipe_data_ != None:
                db.child("user_fav_recipes").child(
                    uid).child(recipe_id).remove()
                db.child("recipe").child(recipe_id).child(
                    "stars").child(uid).remove()
            else:
                db.child("user_fav_recipes").child(
                    uid).child(recipe_id).set(time_liked)
                db.child("recipe").child(recipe_id).child(
                    "stars").child(uid).set(time_liked)
            if navigate == "/recipe_list/":
                navigate += "?page=" + recipes.get_recipes_current_page()
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
                #name = user_info['name']
            #user = auth.refresh(user['refreshToken'])
        except Exception as e:
            # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            print(error['message'])
            msg = error_message(error['message'])
            data = {
                "message": msg
            }
            return render(request, "login.html", {"data": data})
    try:
        if request.session['token_id'] is not None:
            data = {
                "user": user_details
            }
            return render(request, "home.html", {"data": data})
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
        #is_email_valid = validate_email(email_address=email, check_regex=True, check_mx=True, from_address='my@from.addr.ess',helo_host='my.host.name', smtp_timeout=10, dns_timeout=10, use_blacklist=True, debug=True)
        #is_email_valid = validate_email(email, verify=True)
        is_email_valid = True  # validate_email(email, verify=True)
        if is_email_valid:
            register_user(request, email, password, name)
        else:
            msg = error_message("WRONG_EMAIL")
            data = {
                "message": msg
            }
            return render(request, "register.html", {"data": data})

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
        data = {
            "message": msg
        }
        return render(request, "register.html", {"data": data})

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)


@csrf_exempt
def profile(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/")
    else:
        uid = m_user._getUser_Id_()
        user = db.child("users").child(uid).get().val()
        user_details = dict(user)
        m_user._setUser_(user_details)
        data = {
            "user": user_details
        }
        return render(request, "profile.html", {"data": data})


@csrf_exempt
def edit_profile(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/")
    else:
        user_details = m_user._getUser_()
        return render(request, 'edit_profile.html', {"data": user_details})


@csrf_exempt
def personal_recipes(request):
    if m_user._isNone_():
        return render(request, "login.html")
    else:
        chk_ingredients = request.POST.getlist('sav_ing')
        all_ingredients = db.child("all_ingredients").get().val()
        search_ing = request.GET.get('search_ingredients')
        print("search_ingredients: ")
        print(search_ing)

        if search_ing:
            all_ingredients = [i for i in all_ingredients if search_ing in i]
            if not all_ingredients:
                all_ingredients = ["No ingredient found"]
        # research live ingredients
        recipe_details = None
        msg = None
        msg_type = None
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        if request.method == "POST":
            title = request.POST.get("title")
            ingredients = request.POST.get("ingredients")
            description = request.POST.get("description")
            steps = request.POST.get("steps")

            userRecipe = {
                'title': title,
                    'description': description,
                    'steps': steps,
                    'ingredients': ingredients,
                    'privacy': 0
                }
            try:
                db.child("users").child(uid).child("recipes").push(userRecipe)
                my_recipes = db.child("users").child(uid).child("recipes").get()
                #print(dict(my_recipes.each()))
                msg = "Your new recipe is saved successfully."
                msg_type = "success"
            except:
                msg = "An Error occurred."
                msg_type = "error"

                #context = {"ingredients": all_ingredients}
        data = {
            "user": user,
            "message": msg,
            "msg_type": msg_type,
            "ingredients": all_ingredients,

        }
        return render(request, 'personal_recipes.html', {"data": data})


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

    return render(request, 'edit_profile.html', {"data": user_details, "message": msg, "msg_type": msg_type})


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

    return render(request, 'account_settings.html', {"data": user_details, "message": msg, "msg_type": msg_type})


@csrf_exempt
def user_fav_recipes(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        fav_recipes_list = []
        fav_recipes = db.child("user_fav_recipes").child(uid).get()
        num_of_fav_recipes = 0
        if fav_recipes.each() != None:
            for recipe in fav_recipes.each():
                _key_ = str(recipe.key())
                user_fav_recipe = db.child("recipe").child(_key_).get().val()
                if user_fav_recipe:
                    recipe_details = dict(user_fav_recipe)
                    recipe_details["user_saved"] = True
                    recipe_details["recipe_id"] = _key_
                    fav_recipes_list.append(recipe_details)

        num_of_fav_recipes = len(fav_recipes_list)
        data = {
            "user": user,
            "fav_recipes": fav_recipes_list,
            "num_of_fav_recipes": num_of_fav_recipes,
        }

        return render(request, 'user_fav_recipes.html', {"data": data})


# User Error Messages Display
def error_message(type):
    return {
        "EMAIL_EXISTS": "This email is already in use. Try a different email!",
        "WEAK_PASSWORD": "Password should be at least 6 characters.",
        "INVALID_EMAIL": "The email you provided is invalid.",
        "INVALID_PASSWORD": "The password you provided for this email is wrong. Click on Forgot Password to recover your account.",
        "EMAIL_NOT_FOUND": "This email does not exist anywhere on our services.",
        "WRONG_EMAIL": "Please make sure you are using a valid email address."

    }.get(type, "An unknown error has occurred")

# logOut


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


@csrf_exempt
def fridge(request):
    uid = None
    if m_user._isNone_():
        fridge_ingredients = None
        return HttpResponseRedirect("/login/")
    else:
        uid = m_user._getUser_Id_()
        #user = m_user._getUser_()
            
    all_ingredients = db.child("all_ingredients").get().val() #sorted(db.child("all_ingredients").get().val()) leave commented until 
    fridge_ingredients = db.child("users").child(uid).child("Fridge").get().val() # database is cleared of null values
    if fridge_ingredients:
        sorted(fridge_ingredients)

    search_ing = request.GET.getlist('search_ingredients')
   
    chk_food = request.POST.getlist('sav_ing')
    del_food = request.POST.getlist('del_ing')

    if del_food:
        for food in del_food:
            db.child("users").child(uid).child("Fridge").child(food).remove()

    if search_ing:
        all_ingredients = [i for i in all_ingredients if search_ing in i]
        if not all_ingredients:
            all_ingredients = ["No ingredient found"]

    chk_food=['sugar', 'cranberries', 'thyme', 'orange marmalade', 'orange liqueur', 'unsalted butter', 'parmesan', 'black pepper', 'egg yolks', 'purpose flour',
'chicken wings', 'salt', 'chicken base', 'garlic powder', 'ginger powder', 'white pepper', 'egg', 'purpose flour', 'rice flour', 'vegetable', 'dark sugar', 'vinegar', 'oyster sauce', 'soy sauce', 'rice wine', 'honey', 'sesame oil', 'white pepper', 'chili garlic paste', 'spiced water', 'orange slice', 'scallions', 'sesame seeds', 'vegetable', 'garlic', 'chile flakes', 'sichuan peppercorns',
 'brussels sprouts', 'slab bacon', 'lemons', 'grain mustard', 'caraway', 'salt', 'pepper','No ingredients']
    if chk_food and uid:
        new_ingredients= {}
        if fridge_ingredients:
            disj = list(set(chk_food)-set(fridge_ingredients))
            for x in disj:
                new_ingredients[x] =x
            db.child("users").child(uid).child("Fridge").update(new_ingredients)

        else:
            for x in chk_food:
                new_ingredients[x] = x
            db.child("users").child(uid).child("Fridge").set(new_ingredients)

    fridge_ingredients = db.child("users").child(
        uid).child("Fridge").get().val()
    if fridge_ingredients:
        fing_len = len(fridge_ingredients)
    else: 
        fing_len = 0

    btnclick = request.POST.get('serepbt')

    print(btnclick)
    if btnclick:#buttonclick
        all_recipes = db.child("recipe").get().val()
        possible_recipes = []
        for recipe in all_recipes:
            recipe_ingredients = db.child("recipe").child(recipe).child("recipe_ingredients").get().val()
            if set(recipe_ingredients).issubset(set(fridge_ingredients)):
                possible_recipes.append(db.child("recipe").child(recipe).get().val())

        scrollTop = 0
        keep_scroll_pos = False
        if recipes.get_is_recipe_liked():
            scrollTop = recipes.get_recipe_list_position()
            recipes.set_is_recipe_liked(False)
            keep_scroll_pos = True

        # paginator = Paginator(all_recipes, 48)
        # page = request.GET.get('page')
        # recipes.set_recipes_current_page(page)

        # try:
        #     curr_recipes = paginator.page(page)
        # except PageNotAnInteger:
        #     curr_recipes = paginator.page(1)
        # except EmptyPage:
        #     curr_recipes = paginator.page(paginator.num_pages)
        
        
        if possible_recipes:
            data = {
                    "user": m_user._getUser_(),
                    "recipes": possible_recipes,
                    "scrollTop": scrollTop,
                    "keep_scroll_pos": keep_scroll_pos,
                    "found_results": True,
                    "items": len(possible_recipes),
                    "isSearch": True
                }
        else:
            data = {
                    "user": m_user._getUser_(),
                    "recipes": possible_recipes,
                    "scrollTop": scrollTop,
                    "keep_scroll_pos": keep_scroll_pos,
                    "found_results": True,
                    "items":0,
                    "isSearch": True
                }
        
        return render(request, 'recipes.html', {"data": data})

    
    context = {"ingredients" : all_ingredients, 'fing' : fridge_ingredients, "user": m_user._getUser_(),'fing_amount' : fing_len, }
    return render(request, 'fridge.html', context )
    
