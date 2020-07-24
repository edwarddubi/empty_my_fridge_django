from django.shortcuts import render, redirect, HttpResponseRedirect
import pyrebase
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import date
from django.views.decorators.cache import never_cache
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import json
import sys
sys.path.append('..')
sys.path.append('empty_my_fridge/model')
from . import allrecipes
import config
from user import User
from recipes import Recipes
from message import Message
from route import ActivityPage
from category import Category
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


firebase = pyrebase.initialize_app(config.myConfig())

auth_fb = firebase.auth()
fb_storage = firebase.storage()
db = firebase.database()
m_user = User()
m_message = Message()
m_activity = ActivityPage()
m_category = Category()
recipes = Recipes(db, m_user, allrecipes)
recipes._get_all_recipes_()

# Home Page

@csrf_exempt
def home(request):
    if recipes.get_scraped():
        recipes._get_all_recipes_()
        recipes.set_scraped(False)
    if m_user._isNone_():
        return render(request, 'home.html')
    else:
        user = m_user._getUser_()
        data = {
            "user": user,
        }
        return render(request, 'home.html', {"data": data})



@csrf_exempt
def scrape_page(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        uid = m_user._getUser_Id_()
        isAdmin = False
        report = "Your administrative privileges have been verified\n\nScraping...Please wait"
        admins = db.child("admin").child("UPLwshBH98OmbVivV").child("scrapers").get().val()
        for admin in admins:
            if str(admin) == str(uid):
                isAdmin = True
                break
        if isAdmin:
            print(report)
            start = time.time()
            allrecipes.allrecipes(db)
            end = time.time()
            report = "Finished scraping in {0:.2f} min".format((end - start) / 60)
            recipes.set_scraped(True)
        else:
            report = "Your administrative privileges cannot be verified. Failed to scrape."

        data = {
            "report" : report
        }
        return render(request, 'scrape_page.html', {"data" : data})

# get all filtered recipes
def get_all_filtered_recipes():
    recipe_list = []
    uid = m_user._getUser_Id_()
    word = recipes.get_recipe_name_to_find()
    all_recipes = db.child("recipe").get()
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            if recipe.val()["recipe_name"].lower().find(word.lower()) != -1:
                key = str(recipe.key())
                _recipe_ = recipes.get_recipe(dict(recipe.val()), key, uid)
                recipe_list.append(_recipe_)
    return recipe_list

# Recipe Page

@csrf_exempt
def recipe_page(request):
    if recipes.get_scraped():
        recipes._get_all_recipes_()
        recipes.set_scraped(False)
    recipes.set_is_searched_for_recipes(False)
    recipes.set_recipe_name_to_find(None)
    navigate_to_recipe_page = "/empty_my_fridge/recipe_list/"
    navigate_to_recipe_page += "?page=1"
    return HttpResponseRedirect(navigate_to_recipe_page)


@csrf_exempt
def recipe_list(request):
    found_results = False
    isSearch = False
    all_recipes = []
    _recipe_name_ = None
    if recipes.get_is_searched_for_recipes():
        all_recipes = get_all_filtered_recipes()
        isSearch = True
        _recipe_name_ = recipes.get_recipe_name_to_find()
        #recipes.set_is_searched_for_recipes(False)
        if len(all_recipes) != 0:
            found_results = True
    else:
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
            "items": len(all_recipes),
            "isSearch": isSearch,
            "recipe_name" : _recipe_name_,

        }
        return render(request, 'recipes.html', {"data": data})
    else:
        if recipes.get_visited_pages(page) == -1:
            recipes.get_all_likes(m_user._getUser_Id_(), page)
            recipes.set_visited_pages(page)
            
        _user_ = m_user._getUser_()
        data = {
            "user": _user_,
            "recipes": curr_recipes,
            "scrollTop": scrollTop,
            "keep_scroll_pos": keep_scroll_pos,
            "found_results": found_results,
            "items": len(all_recipes),
            "isSearch": isSearch,
            "recipe_name" : _recipe_name_,

        }
        return render(request, 'recipes.html', {"data": data})

def sort_recipes(recipe_list, type):
        result = None
        def fav_sort(recipe):
            try: 
                print(len(recipe["stars"]))
                return len(recipe["stars"])
            except:
                print(0)
                return 0
        if type is "name_A":
            result =  sorted(recipe_list, key = lambda x: x["recipe_name"],reverse=False)
        elif type is "name_D":
            result =  sorted(recipe_list, key = lambda x: x["recipe_name"],reverse=True)
        elif type is "fav_A":
            result =  sorted(recipe_list, key = lambda x: fav_sort(x),reverse=False)
        elif type is "fav_D":
            result =  sorted(recipe_list, key = lambda x: fav_sort(x),reverse=True)
        return result

@csrf_exempt
def category(request):
    cat = request.GET.get('category')
    m_category.set_category(cat)
    found_results = False
    recipe_lst = get_recipes_by_category(cat)
    if len(recipe_lst) != 0:
        found_results = True

    scrollTop = 0
    keep_scroll_pos = False
    if recipes.get_is_recipe_liked():
        scrollTop = recipes.get_recipe_list_position()
        recipes.set_is_recipe_liked(False)
        keep_scroll_pos = True

    paginator = Paginator(recipe_lst, 48)
    page = request.GET.get('page')
    if not page:
        page = "1"
    m_category.set_category_page(page)

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)
    
    user = m_user._getUser_()    
    
    curr_recipes = sort_recipes(curr_recipes,"name_A") or curr_recipes

    data = {
        "user": user,
        "activity" : "categories",
        "recipe_lst": curr_recipes,
        "category": cat,
        "scrollTop": scrollTop,
        "keep_scroll_pos": keep_scroll_pos,
        "found_results": found_results,
        "items": len(recipe_lst),
    }

    return render(request, 'category.html', {"data": data})


def get_recipes_by_category(category):
    all_recipes = db.child('recipe').get()
    uid = m_user._getUser_Id_()
    recipe_lst = []
    for recipe in all_recipes.each():
        recipe_details = recipe.val()
        try:
            categories = recipe_details["recipe_categories"]
            if categories:
                if any(category in c for c in categories) :
                    key = str(recipe.key())
                    _recipe_ = recipes.get_recipe(dict(recipe_details), key, uid)
                    recipe_lst.append(_recipe_)
        except KeyError:
            pass
    return recipe_lst


def get_recipes_by_ingredients(ingredient):
    all_recipes = db.child('recipe').get()
    recipe_lst = []
    uid = m_user._getUser_Id_()
    for recipe in all_recipes.each():
        recipe_details = recipe.val()
        try:
            ingredients = recipe_details["recipe_ingredients"]
            if ingredients:
                if any(ingredient in i for i in ingredients):
                    key = str(recipe.key())
                    _recipe_ = recipes.get_recipe(dict(recipe_details), key, uid)
                    recipe_lst.append(_recipe_)
        except KeyError:
            pass
    return recipe_lst

def get_unique_recipes(categories, ingredients):
    uniques_recipes = []
    for recipe in categories:
        for _recipe_ in ingredients:
            if recipe == _recipe_:
                categories.remove(recipe)

    return categories + ingredients



@csrf_exempt
def get_recipes_by_category_ingredients(request):
    category_list = []
    ingred_list = []
    result_list = []
    found_results = False
    if request.method == "GET":
        value = request.GET.get("category")
        m_category.set_category(value)
        category_list = get_recipes_by_category(value)
        ingred_list = get_recipes_by_ingredients(value)
        result_list = get_unique_recipes(category_list, ingred_list)
        if len(result_list) != 0:
            found_results = True

    scrollTop = 0
    keep_scroll_pos = False
    if recipes.get_is_recipe_liked():
        scrollTop = recipes.get_recipe_list_position()
        recipes.set_is_recipe_liked(False)
        keep_scroll_pos = True

    paginator = Paginator(result_list, 48)
    page = request.GET.get('page')
    if not page:
        page = "1"
    m_category.set_category_page(page)

    try:
        curr_recipes = paginator.page(page)
    except PageNotAnInteger:
        curr_recipes = paginator.page(1)
    except EmptyPage:
        curr_recipes = paginator.page(paginator.num_pages)

    user = m_user._getUser_()
    data = {
        "user": user,
        "activity": "search",
        "recipe_lst": curr_recipes,
        "category": value,
        "scrollTop": scrollTop,
        "keep_scroll_pos": keep_scroll_pos,
        "found_results": found_results,
        "items": len(result_list),
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
        navigate_to_recipe_page = "/empty_my_fridge/recipe_list/"
        if recipes.get_recipes_current_page():
            navigate_to_recipe_page += "?page=" + recipes.get_recipes_current_page()
        else:
            navigate_to_recipe_page += "?page=1"   
    return HttpResponseRedirect(navigate_to_recipe_page)


# Actions (Recipe onClick)
@csrf_exempt
def fav_recipe_onClick(request):
    if m_user._isNone_():
        activity_page = None
        activity_page = request.POST.get("activity")
        if activity_page:
            activity_page = "/empty_my_fridge/login/?activity={0}".format(activity_page)
        else:
            activity_page = "/empty_my_fridge/login/"
            
        return HttpResponseRedirect(activity_page)
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
            _recipe_data_ = db.child("user_fav_recipes").child(
                uid).child(recipe_id).get().val()
            if _recipe_data_ != None:
                recipes.set_recipe_unLiked(recipe_id)
                db.child("user_fav_recipes").child(
                    uid).child(recipe_id).remove()
                db.child("recipe").child(recipe_id).child("stars").child(uid).remove()
            else:
                recipes.set_recipe_liked(recipe_id)
                db.child("user_fav_recipes").child(
                    uid).child(recipe_id).set(time_liked)
                db.child("recipe").child(recipe_id).child(
                    "stars").child(uid).set(time_liked)
            if navigate == "/empty_my_fridge/recipe_list/":
                navigate += "?page=" + recipes.get_recipes_current_page()
            if navigate == "/empty_my_fridge/categories/" or navigate == "/empty_my_fridge/search/":
                navigate += "?category=" + m_category.get_category() + "&page=" + m_category.get_category_page()
            
            return HttpResponseRedirect(navigate)

@csrf_exempt
def upload_image(request):
    file = request.FILES['img']
    uid = m_user._getUser_Id_()
    if uid:
        _dir_ = "images/{0}/{1}".format(uid, file.name)
        img_details = fb_storage.child(_dir_).put(file, request.session['token_id'])
        link = fb_storage.child(_dir_).get_url(img_details["downloadTokens"])

        userData = {
            'image': link,
        }
        db.child("users").child(uid).update(userData)
        _user_ = dict(db.child("users").child(uid).get().val())
        m_user._setUser_(_user_)
        
    return HttpResponseRedirect('/empty_my_fridge/edit_profile/')


##Authentication (Login and Register)
@csrf_exempt
def login(request):
    activity_page = None
    cat = None
    if request.method == 'GET':
        activity_page = request.GET.get("activity")
        cat = request.GET.get("category")
        if not cat:
            cat = m_category.get_category()
    if not activity_page:
        activity_page = m_activity.get_activity_page()
        if not activity_page:
            activity_page = "home"
            
    data = {
        "activity": activity_page,
        "category": cat,
    }
    m_activity.set_activity_page(None)  
    return render(request, 'login.html', {"data":data})


@csrf_exempt
def _login_(request):
    activity_page = None
    if request.method == 'GET':
        email = request.GET.get('email')
        password = request.GET.get('pass')
        activity_page = request.GET.get("activity")
        cat = request.GET.get("category")
        if activity_page == "recipe_list":
            page = recipes.get_recipes_current_page()
            activity_page = "/empty_my_fridge/{0}/?page={1}".format(activity_page, page)
        elif (activity_page == "categories" or activity_page == "search") and cat != "None":
            page = m_category.get_category_page()
            activity_page = "/empty_my_fridge/{0}/?category={1}&page={2}".format(activity_page, cat, page)     
        elif not activity_page:
            activity_page = "/empty_my_fridge/home/"
        else:
            activity_page = "/empty_my_fridge/{0}/".format(activity_page)
        
        try:
            user = auth_fb.sign_in_with_email_and_password(email, password)
            if user != None:
                user = auth_fb.refresh(user['refreshToken'])
                uid = user["userId"]
                user_info = auth_fb.get_account_info(user['idToken'])
                is_verified = user_info["users"][0]["emailVerified"]
                if is_verified:
                    _user_ = db.child("users").child(uid).get().val()
                    m_user._setUser_Id_(uid)
                    user_details = dict(_user_)
                    m_user._setUser_(user_details)
                    request.session['token_id'] = user['idToken']
                    request.session['uid'] = uid
                else:
                    try:
                        del request.session['token_id']
                        del request.session["uid"]
                    except KeyError:
                        pass
                    auth_fb.send_email_verification(user['idToken'])
                    auth.logout(request)
                    msg = error_message('NOT_VERIFIED')
                    data = {
                        "message": msg
                    }
                    
                    return render(request, "login.html", {"data": data})
                
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
    return HttpResponseRedirect(activity_page)


@csrf_exempt
def register(request):
    return render(request, 'register.html')


@csrf_exempt
def _register_(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')
        name = request.POST.get('name')
        data = {
            "message": "A verification link was sent to your email. Please, follow the link to verify your email.",
            "msg_type" : "success"
        }
        try:
            user = auth_fb.create_user_with_email_and_password(email, password)
            user['displayName'] = name
            uid = user['localId']
            email = user['email']
            index_of_at = email.find("@")
            username = email[:index_of_at] + uid[:5]
            today = date.today()
            joined = today.strftime("%B %d, %Y")

            userData = {
                'name': name,
                'email': email,
                'joined': joined,
                'userID': uid,
                'username': username.lower(),
                'image': 'https://react.semantic-ui.com/images/wireframe/square-image.png'
            }
            db.child('users').child(uid).set(userData)
            auth_fb.send_email_verification(user["idToken"])

        except Exception as e:
            # logging.exception('')
            response = e.args[0].response
            error = response.json()['error']
            msg = error_message(error['message'])
            data["message"] = msg
            data["msg_type"] = "error" 

        return render(request, "register.html", {"data": data})

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)


@csrf_exempt
def profile(request):
    if m_user._isNone_():
        m_activity.set_activity_page("profile")
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
        m_activity.set_activity_page("edit_profile")
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        data = {
            'user' : user,
        }
        return render(request, 'edit_profile.html', {"data": data})

@csrf_exempt
def personal_recipes(request):
    recipe_details = None
    msg = None
    msg_type = None
    userRecipe = None
    no_rec = None

    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/") 
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        my_recipes = db.child("users").child(uid).child("recipes").get().val()
        if not my_recipes:
            print("NO RECIPES")
            no_rec = "There are no recipes to show... use the form on the left to add some!"

        if request.method == "POST":
            title = request.POST.get("title")
            ingredients = request.POST.get("search_ingredients").split(",")
            description = request.POST.get("description")
            steps = request.POST.get("steps")
            privacy = request.POST.get("privacy")
            userRecipe = {
            'title': title,
            'description': description,
            'steps': steps,
            'ingredients': ingredients,
            'privacy': privacy
            }
            
            if my_recipes:
                my_recipes.append(userRecipe)
                db.child("users").child(uid).child("recipes").set(my_recipes)
                msg = "Changes saved successfully."
                msg_type = "success"
            else:
                userRecipe = [userRecipe]
                db.child("users").child(uid).child("recipes").set(userRecipe)
                pass
    #context = {"ingredients": all_ingredients}
    my_recipes = db.child("users").child(uid).child("recipes").get().val()
    data = {
        "user": user,
        "message": msg,
        "msg_type": msg_type,
    }
    return render(request, 'personal_recipes.html', {"data": data, "my_recipes": my_recipes, "no_rec": no_rec})



@csrf_exempt
def save_profile(request):
    user_details = m_user._getUser_()
    uid = m_user._getUser_Id_()
    msg = error_message("err")
    msg_type = "error"
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
    data = {
        'user': user_details,
        "message": msg,
        "msg_type": msg_type
    }

    return render(request, 'edit_profile.html', {"data": data})


@csrf_exempt
def account_settings(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user_details = m_user._getUser_()
        uid = m_user._getUser_Id_()
        isAdmin = False
        admins = db.child("admin").child("UPLwshBH98OmbVivV").child("scrapers").get().val()
        for admin in admins:
            if str(admin) == str(uid):
                isAdmin = True
                break
        data = {
            'user': user_details,
            'admin' : isAdmin,
            "msg_type": m_message.get_msg_type(),
            "message" : m_message.get_message()
        }
        m_message.set_message(None)
        m_message.set_msg_type(None)
        return render(request, 'account_settings.html', {"data": data})

@csrf_exempt
def reset_password(request):
    data = {
        "msg_type": m_message.get_msg_type(),
        "message" : m_message.get_message()
    }
    m_message.set_message(None)
    m_message.set_msg_type(None) 
    return render(request, 'reset_password_page.html', {"data" : data})

@csrf_exempt
def recover_password(request):
    msg = error_message("err")
    msg_type = "error"
    email = request.POST.get("email")
    activity = request.POST.get("activity")
    try:
        auth_fb.send_password_reset_email(email)
        msg = "A password recovery link has been sent to your email."
        msg_type = "success"
    except Exception as e:
        response = e.args[0].response
        error = response.json()['error']
        msg = error_message(error['message'])

    activity = '/empty_my_fridge/{0}/'.format(activity)    
    m_message.set_message(msg)
    m_message.set_msg_type(msg_type)    

    return HttpResponseRedirect(activity)


@csrf_exempt
def user_fav_recipes(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
   
    if type.find("WEAK_PASSWORD") != -1:
        type = "WEAK_PASSWORD"  

    if type.find("TOO_MANY_ATTEMPTS_TRY_LATER") != -1:
        type = "TOO_MANY_ATTEMPTS_TRY_LATER"
        
    return {
        "EMAIL_EXISTS": "This email is already in use. Try a different email!",
        "WEAK_PASSWORD": "Password should be at least 6 characters.",
        "INVALID_EMAIL": "Either your email or password is incorrect. Try again.",
        "INVALID_PASSWORD": "Either your email or password is incorrect. Try again.",
        "EMAIL_NOT_FOUND": "This email does not exist anywhere on our services.",
        "WRONG_EMAIL": "Please make sure you are using a valid email address.",
        "NOT_VERIFIED" : "Your email is not verified! Please, follow the link in your email to verify your account.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "There have been too many unsuccessful login attempts. Please try again later."

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
    except KeyError:
        pass
    auth.logout(request)
    return HttpResponseRedirect("/empty_my_fridge/home/")

def Fridge_matches(all_recipes):
        all_recipes = db.child("recipe").get()
        uid = m_user._getUser_Id_()
        possible_recipes = []
        partial_recipes = []
        fridge_ingredients = db.child("users").child(uid).child("Fridge").get().val() # database is cleared of null values

        for recipe in all_recipes.each():
            recipe_details = recipe.val()
            #this code takes long to get the recipe per ingredient
            """
            recipe_ingredients = db.child("recipe").child(recipe).child("recipe_ingredients").get().val()
            if set(recipe_ingredients).issubset(set(fridge_ingredients)):
                possible_recipes.append(db.child("recipe").child(recipe).get().val())
            """
            #this is an optimization and doesn't take long
            try:
                recipe_ingredients = recipe_details["recipe_ingredients"]
                r_i = set(recipe_ingredients)
                f_i = set(fridge_ingredients)
                if r_i.issubset(f_i):
                    key = str(recipe.key())
                    possible_recipes.append(recipes.get_recipe(dict(recipe_details), key, uid))
                elif(len(missing:=(r_i-f_i))<3):
                    key = str(recipe.key())
                    recp = recipes.get_recipe(dict(recipe_details), key, uid)
                    
                    partial_recipes.append((recp,list(missing)))

            except KeyError:
                pass 
            
        print("pos\n", possible_recipes)  
        print("par",len(partial_recipes),"\n", partial_recipes)
        return({"exact":possible_recipes,"partial":partial_recipes})
        return partial_recipes

@csrf_exempt
def fridge(request):
    uid = None
    if m_user._isNone_():
        fridge_ingredients = None
        m_activity.set_activity_page("fridge")
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        uid = m_user._getUser_Id_()
        #user = m_user._getUser_()
    
    all_ingredients = []
    _all_ingredients_ = db.child("all_ingredients").get().val()
    for ingredient in _all_ingredients_:
        if ingredient:
            all_ingredients.append(ingredient)
    
    if len(all_ingredients) > 0:
        all_ingredients = sorted(all_ingredients)
    fridge_ingredients = db.child("users").child(uid).child("Fridge").get().val() # database is cleared of null values
    if fridge_ingredients:
        fridge_ingredients = sorted(fridge_ingredients)

    search_ing = request.GET.get('search_ingredients')
   
    chk_food = request.POST.getlist('sav_ing')
    del_food = request.POST.getlist('del_ing')
    
    #all_ingredients = all_ingredients[:50]
    
    if del_food:
        for food in del_food:
            db.child("users").child(uid).child("Fridge").child(food).remove()
 
    if search_ing:
        all_ingredients = [i for i in all_ingredients if search_ing in i]
        if not all_ingredients:
            all_ingredients = ["No ingredient found"]
   
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

    fridge_ingredients = db.child("users").child(uid).child("Fridge").get().val()
    if fridge_ingredients:
        fing_len = len(fridge_ingredients)
    else: 
        fing_len = 0

    btnclick = request.POST.get('find_Recipe')

    print(btnclick)
    if btnclick:#buttonclick
        
        all_recipes = db.child("recipe").get()

        matches = Fridge_matches(all_recipes)
        possible_recipes = matches["exact"]
        partial = matches["partial"]
        partial_recipes = []
        for tup in partial:
            partial_recipes.append(tup[0])

        scrollTop = 0
        keep_scroll_pos = False
        found_results = False
        if recipes.get_is_recipe_liked():
            scrollTop = recipes.get_recipe_list_position()
            recipes.set_is_recipe_liked(False)
            keep_scroll_pos = True

        if len(possible_recipes) > 0:
            found_results = True

        scrollTop = 0
        keep_scroll_pos = False
        if recipes.get_is_recipe_liked():
            scrollTop = recipes.get_recipe_list_position()
            recipes.set_is_recipe_liked(False)
            keep_scroll_pos = True

        total_recipes = possible_recipes + partial_recipes
        paginator = Paginator(total_recipes, 48)
        page = request.GET.get('page')
        if not page:
            page = "1"
        m_category.set_category_page(page)

        try:
            curr_recipes = paginator.page(page)
        except PageNotAnInteger:
            curr_recipes = paginator.page(1)
        except EmptyPage:
            curr_recipes = paginator.page(paginator.num_pages)
        data = {
            "user": m_user._getUser_(),
            "recipes": curr_recipes,
            "scrollTop": scrollTop,
            "exact_num": len(possible_recipes),
            "keep_scroll_pos": keep_scroll_pos,
            "found_results": found_results,
            "items": len(curr_recipes),
            "isSearch": True
        }
        
        return render(request, 'fridge_recipes.html', {"data": data})

    
    context = {"ingredients" : all_ingredients, 'fing' : fridge_ingredients, "user": m_user._getUser_(),'fing_amount' : fing_len, }
    return render(request, 'fridge.html', context )

    