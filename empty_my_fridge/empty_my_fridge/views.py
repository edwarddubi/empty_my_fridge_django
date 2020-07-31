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

try:
    from empty_my_fridge.model.user import User
except ModuleNotFoundError:
    from empty_my_fridge.empty_my_fridge.model.user import User

from . import food_network
try:
    from empty_my_fridge.empty_my_fridge.model.recipes import Recipes
except ModuleNotFoundError:
    from empty_my_fridge.model.recipes import Recipes

import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

firebase = pyrebase.initialize_app(config.myConfig())

fb_storage = firebase.storage()
auth_fb = firebase.auth()
db = firebase.database()
m_user = User()
recipes = Recipes(db, m_user, food_network)
recipes._get_all_recipes_()

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



@csrf_exempt
def scrape_page(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        uid = m_user._getUser_Id_()
        isAdmin = False
        report = "Your Administrative privileges have been verified\n\nScraping...Please wait"
        admins = db.child("admin").child("UPLwshBH98OmbVivV").child("scrapers").get().val()
        for admin in admins:
            if str(admin) == str(uid):
                isAdmin = True
                break
        if isAdmin:
            print(report)    
            db.child('all_ingredients').remove()
            food_network.food_network(db)
        else:
            report = "Your Administrative privileges cannot been verified. Failed to Scrape"

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
    if recipes.get_is_searched_for_recipes():
        all_recipes = get_all_filtered_recipes()
        isSearch = True
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
        "recipe_lst": curr_recipes,
        "category": cat,
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


@csrf_exempt
def get_recipes_by_category_ingredients(request):
    category_list = []
    ingred_list = []
    result_list = []
    if request.method == "GET":
        value = request.GET.get("category")
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
        "recipe_lst": curr_recipes,
        "category": value,
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
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
                db.child("recipe").child(recipe_id).child(
                    "stars").child(uid).remove()
            else:
                recipes.set_recipe_liked(recipe_id)
                db.child("user_fav_recipes").child(
                    uid).child(recipe_id).set(time_liked)
                db.child("recipe").child(recipe_id).child(
                    "stars").child(uid).set(time_liked)
            if navigate == "/empty_my_fridge/recipe_list/":
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
            return HttpResponseRedirect("/empty_my_fridge/home/")
    except KeyError:
        return HttpResponseRedirect("/empty_my_fridge/login/")


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
        else:
            msg = error_message("WRONG_EMAIL")
            data = {
                "message": msg
            }
            return render(request, "register.html", {"data": data})

    return HttpResponseRedirect("/empty_my_fridge/login/")

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)

# Profile Page (Profile--about me, Edit Profile and Save new profile information, Account Settings, Recover Password, User Favorite Recipes)


@csrf_exempt
def profile(request):
    if m_user._isNone_():
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
def public_profile(request):
    user_details = {}
    pUser_details = {}
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        #set the user that's still logged in
        uid = m_user._getUser_Id_()
        user = db.child("users").child(uid).get().val()
        user_details = dict(user)
        m_user._setUser_(user_details)


        #if a user was posted (which is the only way to get to this page),
        #   then, grab that user's ID and return an object with that user's info
        print("request.method: ")
        print(request.method)
        friend_id = request.GET.get("id")
        print(friend_id)
        m_user.set_myFriend_id(friend_id)

        if friend_id:
            pUser = db.child("users").child(friend_id).get().val()
            print("pUser: ")
            print(pUser)
            pUser_details = dict(pUser)
            #pUser._setUser_(user_details)
    data = {
        "user": user_details,
        "pUser": pUser_details
    }
    return render(request, "public_profile.html", {"data": data})


@csrf_exempt
def edit_profile(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user_details = m_user._getUser_()
        return render(request, 'edit_profile.html', {"data": user_details})

@csrf_exempt
def public_personal_recipes(request):
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
        friend_id = m_user.get_myFriend_id()
        pUser = db.child("users").child(friend_id).get().val()

        my_recipes = db.child("users").child(friend_id).child("recipes").get().val()
        if not my_recipes:
            no_rec = "Looks like they don't have any personal recipes at the moment..."
    data = {
        "user": user,
        "pUser": pUser,
        "message": msg,
        "msg_type": msg_type,
    }
    return render(request, 'public_personal_recipes.html', {"data": data, "my_recipes": my_recipes, "no_rec": no_rec})

@csrf_exempt
def personal_recipes(request):
    recipe_details = None
    msg = None
    msg_type = None
    userRecipe = None
    no_rec = None
    my_recipes = []
    my_recipe_list = []
    link = "https://firebasestorage.googleapis.com/v0/b/empty-my-fridge-ff73c.appspot.com/o/cutePlate.jpg?alt=media&token=229f016f-e151-4bf7-b569-d6a07a6a2c18"

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
            print(title)
            if not title:
                recipe_id = request.POST.get("delete_recipe")
                print(recipe_id)
                db.child("users").child(uid).child("recipes").child(recipe_id).remove()
                db.child("recipe").child(recipe_id).remove()
            else:
                ingredients = request.POST.get("ingredients").split(",")
                measurements = request.POST.get("measurements").split(",")
                
                if len(ingredients) == len(measurements):
                    r_key = db.generate_key()
                    description = request.POST.get("description")
                    recipe_categories = request.POST.get("recipe_categories").split(",")
                    steps = request.POST.get("steps").splitlines()
                    privacy = request.POST.get("privacy")
                    clicked = request.POST.get("rec_link")

                    userRecipe = {
                    'recipe_name': title,
                    'recipe_id': r_key,
                    'description': description,
                    'recipe_categories': recipe_categories,
                    'steps': steps,
                    'recipe_ingredients': ingredients,
                    'measurements': measurements,
                    'privacy': privacy,
                    'recipe_image': link,
                    'uid': uid
                    }
                    if privacy == "2":
                        thisIng = db.child("all_ingredients").get().val()
                        if thisIng:
                            thisIng = list(dict.fromkeys(thisIng+ingredients))
                        else:
                            thisIng = ingredients
                        
                        db.child("all_ingredients").set(thisIng)
                        db.child("recipe").child(r_key).set(userRecipe)
                    
                    db.child("users").child(uid).child("recipes").child(r_key).set(userRecipe)
                    
                    msg = "Your recipe has been created!"
                    msg_type = "success"
                else:
                    msg = "Looks like you're missing an ingredient or a measurement... try again!"
                    msg_type = "error"

    my_recipes = db.child("users").child(uid).child("recipes").get().each()

    if my_recipes:
        for recipe in my_recipes:
            recipe_details = recipe.val()
            key = str(recipe.key())
            recipe_details["recipe_id"] = key
            my_recipe_list.append(recipe_details)
    
    data = {
        "user": user,
        "message": msg,
        "msg_type": msg_type,
    }
    return render(request, 'personal_recipes.html', {"data": data, "my_recipes": my_recipe_list, "no_rec": no_rec})



@csrf_exempt
def user_friends(request):
    remove = False
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friends_list = []
        friends = db.child("users").child(uid).child("friends").get().val()
        num_of_friends = 0
        if friends.items() != None:
            for _key_,value in friends.items():
                #_key_ = str(fren.key()) #grabs friend's unique id
                thisFren = db.child("users").child(_key_).get().val() #what does .val() do at the end?
                #nt(value["added_back"])
                if value["added_back"] == "True":
                    friend_details = dict(thisFren)
                    # print(friend_details)
                    friends_list.append(friend_details)

        if request.method == "POST":
            print("is being DELETED...")
            deny = request.POST.get("deny")
            thisFren = db.child("users").child(deny).get().val() #what does .val() do at the end?
            #once you find the right person...
            if thisFren:
                #delete them from my friend list...
                db.child("users").child(uid).child("friends").child(deny).remove()
                remove = True
                return HttpResponseRedirect("/empty_my_fridge/friends/")
        
        num_of_friends = len(friends_list)
        data = {
            "user": user,
            "friends": friends_list,
            "num_of_friends": num_of_friends
        }

        return render(request, 'friends.html', {"data": data})

@csrf_exempt
def public_friends(request):
    remove = False
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        #get friend's object
        friend_id = request.GET.get("id")
        print("friend_id: ")
        print(friend_id)

        if friend_id:
            pUser = db.child("users").child(friend_id).get().val()
            # print("pUser: ")
            # print(pUser)
            pUser_details = dict(pUser)
            #pUser._setUser_(user_details)

        friends_list = []
        friends = db.child("users").child(friend_id).child("friends").get().val()
        print("has friends: ")
        print(friends)
        num_of_friends = 0
        if friends.items() != None:
            for _key_,value in friends.items():
                print("key")
                print(_key_)
                #_key_ = str(fren.key()) #grabs friend's unique id
                #added_back"])
                if value["added_back"]:
                    thisFren = db.child("users").child(_key_).get().val()
                    friend_details = dict(thisFren)
                    # print(friend_details)
                    friends_list.append(friend_details)
        print(friends_list)
        num_of_friends = len(friends_list)
        data = {
            "user": user,
            "pUser": pUser,
            "friends": friends_list,
            "num_of_friends": num_of_friends
        }

        return render(request, 'public_friends.html', {"data": data})

@csrf_exempt
def friend_requests(request):
    print("in friend_request!")
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        users = db.child("users").get()
        found = False
        isSent = False
        isSub = False
        thisUser = None
        friend_added = False
        friend_deleted = False

        friends_list = []
        friends = db.child("users").child(uid).child("friends").get().val()
        #print(friends)
        num_of_friends = 0
    

        #we're posting an email or id to check
        if request.method == "POST":
            friends = db.child("users").child(uid).child("friends").get().val()
            
            isSent = True
            email = request.POST.get("email")
            username = request.POST.get("username")
            accept = request.POST.get("accept")
            print("accept: ")
            print(accept)
            deny = request.POST.get("deny")
            print("deny: ")
            print(deny)
            #they chose to use email....
            if email:
                #thisUser = db.child("users").order_by_child("email").equal_to(email).get()
                for person in users.each():
                    person = dict(person.val())
                    if person["email"] == email:
                        thisUser = person
                        break
            elif username:
                #thisUser = db.child("users").order_by_child("username").equal_to(username).get()
                for person in users.each():
                    person = dict(person.val())
                    if person["username"] == username:
                        thisUser = person
                        break
            if accept:
                isSub = True
                print("is being ADDED.... ")
                #so if you actually have friends...
                #if friends:
                    #look through them...
                   # for fren in friends.each():
                thisFren = db.child("users").child(uid).child("friends").child(accept).get().val() #what does .val() do at the end?
                print("thisFren: ")
                print(thisFren)
                #set them true on my friend list...
                db.child("users").child(uid).child("friends").child(accept).update({"added_back": "True"})
               # thisFren["added_back"] = True
                
                #and add me as a friend on theirs...
                me = dict(user)
                me = {
                    "added_back": True,
                    "userID": uid
                }
                db.child("users").child(accept).child("friends").child(uid).set(me)
                friend_added = True
            if deny:
                isSub = True
                print("is being DELETED...")
                thisFren = db.child("users").child(deny).get().val() #what does .val() do at the end?
                #once you find the right person...
                if thisFren:
                    #delete them from my friend list...
                    db.child("users").child(uid).child("friends").child(deny).remove()
                    friend_deleted = True
            #print(thisUser)

            if thisUser:
                #thisEmail = thisUser["email"]
                #once we've found the right user, add us to their friends list!
                _key_ = thisUser["userID"] #grabs person's unique id
                thisFren = db.child("users").child(_key_).get().val()
                if thisFren:
                    me = {
                        "added_back": False,
                        "userID": uid
                    }
                    # me["added_back"] = False
                    # me["user_id"] = uid
                    # their_friends.append(me)
                    
                    db.child("users").child(_key_).child("friends").child(uid).set(me)
                    found = True
            return HttpResponseRedirect("/empty_my_fridge/friend_requests/")
            #they chose to use userID...
        print(friends)
        if friends:
            for key, value in friends.items():
                thisFren = db.child("users").child(key).get().val()
 
                #once you find the right person...
                if value["added_back"] == "False":
                    friends_list.append(dict(thisFren))
        num_of_friends = len(friends_list)
        print("isSent: ")
        print(isSent)
        print("isSub: ")
        print(isSub)
        #print(found)
        data = {
            "user": user,
            "found": found,
            "isSent": isSent,
            "isSub": isSub,
            "friends": friends_list,
            "num_of_friends": num_of_friends,
            "friend_added": friend_added,
            "friend_deleted": friend_deleted
        }
    
    return render(request, 'friend_requests.html', {"data": data})

@csrf_exempt
def add_friend(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friends_list = []
        friends = db.child("users").child(uid).child("friends").get()
        if request.method == "POST":
            frenID = request.POST.get("frenID")
            if friends.each() != None:
                for fren in friends.each():
                    _key_ = str(fren.key()) #grabs friend's unique id
                    thisFren = db.child("users").child(_key_).get().val() #what does .val() do at the end?
                    #once you find the right person...
                    if thisFren["userID"] == frenID:
                        #add them to my friend list...
                        friends_list.remove(fren)
                        their_friends = db.child("users").child(uid).child("friends").get()
                        
                        #and add me to theirs...
                        me = dict(user)
                        me["added_back"] = True
                        me["user_id"] = uid
                        their_friends.append(me)
                        friend_added = True


        
        data = {
            "user": user,
            "friend_added": friend_added
        }

        return render(request, 'friends.html', {"data": data})

@csrf_exempt
def delete_friend(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friends_list = []
        friends = db.child("users").child(uid).child("friends").get()
        friend_deleted = False
        if request.method == "POST":
            frenID = request.POST.get("frenID")
            if friends.each() != None:
                for fren in friends.each():
                    _key_ = str(fren.key()) #grabs friend's unique id
                    thisFren = db.child("users").child(_key_).get().val() #what does .val() do at the end?
                    #once you find the right person...
                    if thisFren["userID"] == frenID:
                        #remove them from my friend list...
                        friends_list.remove(fren)
                        their_friends = db.child("users").child(uid).child("friends").get()
                        
                        #and remove me from theirs...
                        me = dict(user)
                        me["added_back"] = True
                        me["user_id"] = uid
                        their_friends.remove(me)
                        friend_added = True


        
        data = {
            "user": user,
            "friend_added": friend_added
        }

        return render(request, 'friends.html', {"data": data})

@csrf_exempt
def recipe_format(request):
    user = m_user._getUser_()
    uid = m_user._getUser_Id_()
    print_list = []
    recipe_id = request.GET.get("id")
    print(recipe_id)
    link = None
    #"https://firebasestorage.googleapis.com/v0/b/empty-my-fridge-ff73c.appspot.com/o/cutePlate.jpg?alt=media&token=229f016f-e151-4bf7-b569-d6a07a6a2c18"

    if request.method == "POST":
        # recipe_id = request.POST.get("recipe_id")
        # print(recipe_id)
        try:
            file = request.FILES['img']
            print("file: ")
            print(file.name)
            
            _dir_ = "recipe_images/{0}/{1}".format(uid, file.name)
            img_details = fb_storage.child(_dir_).put(file, request.session['token_id'])
            link = fb_storage.child(_dir_).get_url(img_details["downloadTokens"])
        except Exception:
            pass

    recipe_image_update = {
            "recipe_image": link
        }
    this_recipe = db.child("recipe").child(recipe_id).get().val()
    print(this_recipe)
    print(link)
    if this_recipe and link:
         db.child("recipe").child(recipe_id).update(recipe_image_update)
         db.child("users").child(uid).child("recipes").child(recipe_id).update(recipe_image_update)
         this_recipe["recipe_image"] = link

    elif not this_recipe and link:
    
        db.child("users").child(uid).child("recipes").child(recipe_id).update(recipe_image_update)

    if not this_recipe:
        this_recipe = db.child("users").child(uid).child("recipes").child(recipe_id).get().val()

    try:
        if uid:
            if this_recipe["uid"] == uid:
                this_recipe["belongsToUser"] = True
    except KeyError:
        pass
    for (measurement, ingredient) in zip(this_recipe["measurements"], this_recipe["recipe_ingredients"]):
        combo = measurement + ": " + ingredient
        print_list.append(combo)
    
    print("Recipe")
    
    data = {
        "recipe": this_recipe,
        "ingredients": print_list,
        "recipe_id": recipe_id
    }
    return render(request, 'recipe_format.html', {"data": data})


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

    return render(request, 'edit_profile.html', {"data": user_details, "message": msg, "msg_type": msg_type})


@csrf_exempt
def account_settings(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
        return HttpResponseRedirect("/empty_my_fridge/login/")
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
def public_fav_recipes(request):
    if m_user._isNone_():
            return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friend_id = m_user.get_myFriend_id()
        pUser = db.child("users").child(friend_id).get().val()
        
        fav_recipes_list = []

        fav_recipes = db.child("user_fav_recipes").child(friend_id).get()
        num_of_fav_recipes = 0
        if fav_recipes.each():
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
            "pUser": pUser,
            "fav_recipes": fav_recipes_list,
            "num_of_fav_recipes": num_of_fav_recipes,
        }

        return render(request, 'public_fav_recipes.html', {"data": data})

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
    return HttpResponseRedirect("/empty_my_fridge/login/")


@csrf_exempt
def fridge(request):
    uid = None
    if m_user._isNone_():
        fridge_ingredients = None
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

    btnclick = request.POST.get('serepbt')

    #print(btnclick)
    if btnclick:#buttonclick
        all_recipes = db.child("recipe").get()
        possible_recipes = []
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
                if set(recipe_ingredients).issubset(set(fridge_ingredients)):
                    key = str(recipe.key())
                    possible_recipes.append(recipes.get_recipe(dict(recipe_details), key, uid))

            except KeyError:
                pass        

        scrollTop = 0
        keep_scroll_pos = False
        found_results = False
        if recipes.get_is_recipe_liked():
            scrollTop = recipes.get_recipe_list_position()
            recipes.set_is_recipe_liked(False)
            keep_scroll_pos = True

        if len(possible_recipes) > 0:
            found_results = True

        paginator = Paginator(possible_recipes, 48)
        page = request.GET.get('page')
        recipes.set_recipes_current_page(page)

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
            "keep_scroll_pos": keep_scroll_pos,
            "found_results": found_results,
            "items": len(possible_recipes),
            "isSearch": True
        }
        
        return render(request, 'fridge_recipes.html', {"data": data})

    
    context = {"ingredients" : all_ingredients, 'fing' : fridge_ingredients, "user": m_user._getUser_(),'fing_amount' : fing_len, }
    return render(request, 'fridge.html', context )
