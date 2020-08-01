from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
import time
from category import Category
from route import ActivityPage
from message import Message
from recipes import Recipes
from user import User
import config
from . import allrecipes




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
    m_category.set_filter_list(None)
    recipes.set_filter_list(None)
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


def Fridge_matches(all_recipes):
    possible_recipes = []
    partial_recipes = []
    fridge_ingredients = db.child("users").child(m_user._getUser_Id_()).child("Fridge").get().val()
    for recipe in all_recipes:
        #recipe_details = recipe.val()
        try:
            recipe_ingredients = recipe["recipe_ingredients"]
            r_i = set(recipe_ingredients)
            if(fridge_ingredients):
                f_i = set(fridge_ingredients)
            else:
                f_i = set()
            if r_i.issubset(f_i):
                possible_recipes.append(recipe)
            elif(len(missing:=(r_i-f_i))<4):
                recipe["missing_ingredients"]=list(missing)
                partial_recipes.append(recipe)
        except KeyError:
            pass
    return({"exact":possible_recipes,"partial":partial_recipes})

def sort_recipes(recipe_list, type):
    try:
        result = None
        if type == "name_A":
            result = sorted(recipe_list, key=lambda x: x["recipe_name"], reverse=False)
        elif type == "name_D":
            result = sorted(recipe_list, key=lambda x: x["recipe_name"], reverse=True)
        elif type == "fav_A":
            result = sorted(recipe_list, key=lambda x: x["likes"], reverse=False)
        elif type == "fav_D":
            result = sorted(recipe_list, key=lambda x: x["likes"], reverse=True)
        return result
    except:
        return None


@csrf_exempt
def scrape_page(request):
    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        uid = m_user._getUser_Id_()
        isAdmin = False
        report = "Your administrative privileges have been verified\n\nScraping...Please wait"
        admins = db.child("admin").child(
            "UPLwshBH98OmbVivV").child("scrapers").get().val()
        for admin in admins:
            if str(admin) == str(uid):
                isAdmin = True
                break
        if isAdmin:
            print(report)
            start = time.time()
            allrecipes.allrecipes(db)
            end = time.time()
            total_time = end - start
            minutes = 0
            while total_time >= 0:
                if total_time - 60 >= 0:
                    minutes += 1
                total_time -= 60

            seconds = total_time + 60
            report = "Finished scraping in {0} minute(s) and {1:0.1f} seconds.".format(
                minutes, seconds)
            recipes.set_scraped(True)
        else:
            report = "Your administrative privileges cannot be verified. Failed to scrape."

        data = {
            "report": report
        }
        return render(request, 'scrape_page.html', {"data": data})

# get all filtered recipes

def get_all_filtered_recipes():
    recipe_list = []
    uid = m_user._getUser_Id_()
    word = recipes.get_recipe_name_to_find()
    all_recipes = db.child("recipe").get()
    if all_recipes.each() != None:
        for recipe in all_recipes.each():
            key = str(recipe.key())
            try:
                if recipe.val()["recipe_name"].lower().find(word.lower()) != -1:
                    _recipe_ = recipes.get_recipe(dict(recipe.val()), key, uid)
                    recipe_list.append(_recipe_)
            except KeyError:
                db.child("recipe").child(key).remove()
                continue
    return recipe_list

# Recipe Page
@csrf_exempt
def recipe_page(request):
    if recipes.get_scraped():
        recipes._get_all_recipes_()
        recipes.set_scraped(False)
    recipes.set_is_searched_for_recipes(False)
    recipes.set_fridge_recipes(None)
    recipes.set_recipe_name_to_find(None)
    recipes.set_filter_list(None)
    navigate_to_recipe_page = "/empty_my_fridge/recipe_list/"
    navigate_to_recipe_page += "?page=1"
    return HttpResponseRedirect(navigate_to_recipe_page)


def unique_filtered_recipes(recipes):
    unique_recipes = []
    for recipe in recipes:
        if recipe not in unique_recipes:
            unique_recipes.append(recipe)
    return unique_recipes


def set_active_filters(filters, removal, isCategory):
    new_filters = []
    new_unique_filters = []
    if isCategory:
        curr_filters = m_category.get_filter_list()
    else:
        curr_filters = recipes.get_filter_list()

    if curr_filters is not None:
        new_filters = curr_filters + filters
        for filter in new_filters:
            if filter not in new_unique_filters:
                new_unique_filters.append(filter)
    else:
        new_unique_filters = filters

    if len(removal) > 0:
        for filter in removal:
            if filter in new_unique_filters:
                new_unique_filters.remove(filter)
    if isCategory:
        m_category.set_filter_list(new_unique_filters)
        recipes.set_filter_list(None)
    else:
        recipes.set_filter_list(new_unique_filters)
        m_category.set_filter_list(None)


@csrf_exempt
def filter(recipe_list, filter_list, isComplete):
    filtered_recipes = []
    duplicate_recipes = []
    started = False

    if isComplete:
        for filter in filter_list:
            if len(filtered_recipes) == 0 and not started:
                started = True
                for recipe in recipe_list:
                    try:
                        categories = recipe["recipe_categories"]
                        if any(filter in f for f in categories):
                            filtered_recipes.append(recipe)
                    except KeyError:
                        pass
            else:
                for recipe in filtered_recipes:
                    try:
                        categories = recipe["recipe_categories"]
                        if not any(filter in f for f in categories):
                            duplicate_recipes.append(recipe)
                    except KeyError:
                        pass
    else:
        for filter in filter_list:
            for recipe in recipe_list:
                try:
                    categories = recipe["recipe_categories"]
                    if any(filter in f for f in categories):
                        filtered_recipes.append(recipe)
                except KeyError:
                    pass
    for duplicate in duplicate_recipes:
        if duplicate in filtered_recipes:
            filtered_recipes.remove(duplicate)
    filtered_recipes = unique_filtered_recipes(filtered_recipes)
    return filtered_recipes


@csrf_exempt
def recipe_list(request):
    found_results = False
    isSearch = False
    isComplete = False
    isRemoving = False
    isClearing = False
    isFilter = False
    to_remove = []
    filters = request.POST.getlist('filter_data')
    remove_list = request.POST.getlist('remove_filter')
    clear_all = request.POST.get('clear')
    curr_filters = recipes.get_filter_list()

    if clear_all:
        isClearing = True

    if isClearing:
        recipes.set_filter_list(None)
    else:
        filter_style = request.POST.get('filter_style')
        if remove_list is not None:
            isRemoving = True
        if filter_style:
            isComplete = True

        if isRemoving:
            if curr_filters is not None:
                for option in remove_list:
                    to_remove.append(option)
        set_active_filters(filters, to_remove, False)

    all_recipes = []
    _recipe_name_ = None
    if recipes.get_is_searched_for_recipes():
        all_recipes = get_all_filtered_recipes()
        isSearch = True
        _recipe_name_ = recipes.get_recipe_name_to_find()
        # recipes.set_is_searched_for_recipes(False)
        if len(all_recipes) != 0:
            found_results = True
    else:
        all_recipes = recipes.get_all_recipes()
    scrollTop = 0
    keep_scroll_pos = False
    fridge_recipes = recipes.get_fridge_recipes()

    disp_fridge = (False, False)
    if request.method == "POST" or fridge_recipes:
        if m_user._isNone_():
                activity_page = "/empty_my_fridge/login/?activity=recipe_list"
                return HttpResponseRedirect(activity_page)
        else:
            uid = m_user._getUser_Id_()
            if (request.POST.get('part')=="True" or fridge_recipes == "part"):
                matches = Fridge_matches(all_recipes)
                fridge_recipes = "part"
                all_recipes = []
                if(matches):
                    all_recipes = matches["partial"]
                    if all_recipes:
                        temp_recipes = []
                        for recipe in all_recipes:
                            try:
                                is_fav = recipe["stars"][uid] != None
                                recipe["user_saved"] = is_fav
                            except KeyError:
                                pass
                            temp_recipes.append(recipe)
                        all_recipes = temp_recipes

                        
                disp_fridge = (True, True)
            elif(fridge_lst:=request.POST.get('fridge')=="True" or fridge_recipes == "fridge"):
                matches = Fridge_matches(all_recipes)
                all_recipes=[]
                fridge_recipes = "fridge"
                if(matches):
                    all_recipes = matches["exact"]
                    if all_recipes:
                        temp_recipes = []
                        for recipe in all_recipes:
                            try:
                                is_fav = recipe["stars"][uid] != None
                                recipe["user_saved"] = is_fav
                            except KeyError:
                                pass
                            temp_recipes.append(recipe)
                        all_recipes = temp_recipes

                disp_fridge = (True, False)
            recipes.set_fridge_recipes(None)
        if(sorting_type:=request.POST.get('sorting')):
            recipes.set_sorting_type(sorting_type)

    all_recipes = sort_recipes(all_recipes, recipes.get_sorting_type()) or all_recipes
    
    if recipes.get_is_recipe_liked():
        scrollTop = recipes.get_recipe_list_position()
        recipes.set_is_recipe_liked(False)
        keep_scroll_pos = True
    filters = recipes.get_filter_list()
    if filters:
        isFilter = True
        all_recipes = filter(all_recipes, filters, isComplete)

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
            "fridge": disp_fridge,
            "sorting_type": recipes.get_sorting_type(),
            "recipe_name": _recipe_name_,
            "active_filters": filters,
            "isFilter": isFilter,
            "fridge_recipes": fridge_recipes,

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
            "fridge": disp_fridge,
            "sorting_type": recipes.get_sorting_type(),
            "recipe_name": _recipe_name_,
            "active_filters": filters,
            "isFilter": isFilter,
            "fridge_recipes": fridge_recipes
        }
        return render(request, 'recipes.html', {"data": data})


@csrf_exempt
def category(request):
    cat = request.GET.get('category')
    isComplete = False
    isRemoving = False
    isClearing = False
    to_remove = []
    filters = request.POST.getlist('filter_data')
    remove_list = request.POST.getlist('remove_filter')
    clear_all = request.POST.get('clear')
    curr_filters = m_category.get_filter_list()

    if clear_all:
        isClearing = True

    if isClearing:
        m_category.set_filter_list(None)
    else:
        filter_style = request.POST.get('filter_style')
        if remove_list is not None:
            isRemoving = True
        if filter_style:
            isComplete = True

        if isRemoving:
            if curr_filters is not None:
                for option in remove_list:
                    to_remove.append(option)
        set_active_filters(filters, to_remove, True)

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
    filters = m_category.get_filter_list()
    if filters:
        recipe_lst = filter(recipe_lst, filters, isComplete)

    fridge_recipes = recipes.get_fridge_recipes()
    disp_fridge = (False, False)
    if request.method == "POST" or fridge_recipes:
        if (request.POST.get('part')=="True" or fridge_recipes == "part"):
            if m_user._isNone_():
                activity_page = "/empty_my_fridge/login/?activity=recipe_list"
                return HttpResponseRedirect(activity_page)
            matches = Fridge_matches(recipe_lst)
            uid = m_user._getUser_Id_()
            fridge_recipes = "part"
            recipe_lst = []
            if(matches):
                recipe_lst = matches["partial"]
                if recipe_lst:
                    temp_recipes = []
                    for recipe in recipe_lst:
                        try:
                            is_fav = recipe["stars"][uid] != None
                            recipe["user_saved"] = is_fav
                        except KeyError:
                            pass
                        temp_recipes.append(recipe)
                    recipe_lst = temp_recipes
            disp_fridge = (True, True)
        elif(fridge_lst:=request.POST.get('fridge')=="True" or fridge_recipes=="fridge"):
            if m_user._isNone_():
                activity_page = "/empty_my_fridge/login/?activity=recipe_list"
                return HttpResponseRedirect(activity_page)
            uid = m_user._getUser_Id_()
            matches = Fridge_matches(recipe_lst)
            fridge_recipes = "fridge"
            recipe_lst = []
            if(matches):
                recipe_lst = matches["exact"]
                if recipe_lst:
                    temp_recipes = []
                    for recipe in recipe_lst:
                        try:
                            is_fav = recipe["stars"][uid] != None
                            recipe["user_saved"] = is_fav
                        except KeyError:
                            pass
                        temp_recipes.append(recipe)
                    recipe_lst = temp_recipes
            disp_fridge = (True, False)
        recipes.set_fridge_recipes(None)
        if(sorting_type:=request.POST.get('sorting')):
            recipes.set_sorting_type(sorting_type)

    
    recipe_lst = sort_recipes(recipe_lst, recipes.get_sorting_type()) or recipe_lst

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

    data = {
        "user": user,
        "activity": "categories",
        "recipe_lst": curr_recipes,
        "category": cat,
        "scrollTop": scrollTop,
        "keep_scroll_pos": keep_scroll_pos,
        "found_results": found_results,
        "items": len(recipe_lst),
        "fridge": disp_fridge,
        "sorting_type": recipes.get_sorting_type(),
        "active_filters": filters,
        "fridge_recipes" : fridge_recipes,
    }
    return render(request, 'category.html', {"data": data})


def get_recipes_by_category(category):
    all_recipes = db.child('recipe').get()
    uid = m_user._getUser_Id_()
    recipe_lst = []
    if all_recipes.each():
        for recipe in all_recipes.each():
            recipe_details = recipe.val()
            try:
                categories = recipe_details["recipe_categories"]
                if categories:
                    if any(category in c for c in categories):
                        key = str(recipe.key())
                        _recipe_ = recipes.get_recipe(
                            dict(recipe_details), key, uid)
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
                    _recipe_ = recipes.get_recipe(
                        dict(recipe_details), key, uid)
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
    value = None
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

    disp_fridge = (False, False)
    if request.method == "POST":
        if (request.POST.get('part')=="True"):
            if m_user._isNone_():
                activity_page = "/empty_my_fridge/login/?activity=recipe_list"
                return HttpResponseRedirect(activity_page)
            matches = Fridge_matches(result_list)
            result_list = []
            uid = m_user._getUser_Id_()
            if(matches):
                result_list = matches["partial"]
                if result_list:
                    temp_recipes = []
                    for recipe in result_list:
                        try:
                            is_fav = recipe["stars"][uid] != None
                            recipe["user_saved"] = is_fav
                        except KeyError:
                            pass
                        temp_recipes.append(recipe)
                    result_list = temp_recipes
            disp_fridge = (True, True)
        elif(fridge_lst:=request.POST.get('fridge')=="True"):
            if m_user._isNone_():
                activity_page = "/empty_my_fridge/login/?activity=recipe_list"
                return HttpResponseRedirect(activity_page)
            matches = Fridge_matches(result_list)
            result_list = []
            uid = m_user._getUser_Id_()
            if(matches):
                result_list = matches["exact"]
                if result_list:
                    temp_recipes = []
                    for recipe in result_list:
                        try:
                            is_fav = recipe["stars"][uid] != None
                            recipe["user_saved"] = is_fav
                        except KeyError:
                            pass
                        temp_recipes.append(recipe)
                    result_list = temp_recipes
            disp_fridge = (True, False)
        if(sorting_type:=request.POST.get('sorting')):
            recipes.set_sorting_type(sorting_type)

    result_list = sort_recipes(result_list, recipes.get_sorting_type()) or result_list
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
        "fridge": disp_fridge,
        "sorting_type": recipes.get_sorting_type(),
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
            recipes.set_filter_list(None)
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
            activity_page = "/empty_my_fridge/login/?activity={0}".format(
                activity_page)
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
            isFridge_recipes = request.POST.get("fridge_recipes")
            if isFridge_recipes:
                recipes.set_fridge_recipes(isFridge_recipes)

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
            elif navigate == "/empty_my_fridge/categories/" or navigate == "/empty_my_fridge/search/":
                navigate += "?category=" + m_category.get_category() + "&page=" + m_category.get_category_page()
            elif navigate == "/empty_my_fridge/public_fav_recipes/":
                navigate += "?id=" + m_user.get_friend_id()

            return HttpResponseRedirect(navigate)


@csrf_exempt
def upload_image(request):
    try:
        file = request.FILES['img']
        uid = m_user._getUser_Id_()
        if uid:
            _dir_ = "images/{0}/{1}".format(uid, file.name)
            img_details = fb_storage.child(_dir_).put(
                file, request.session['token_id'])
            link = fb_storage.child(_dir_).get_url(
                img_details["downloadTokens"])

            userData = {
                'image': link,
            }
            db.child("users").child(uid).update(userData)
            _user_ = dict(db.child("users").child(uid).get().val())
            m_user._setUser_(_user_)
    except Exception:
        pass

    return HttpResponseRedirect('/empty_my_fridge/edit_profile/')


##Authentication (Login and Register)
@csrf_exempt
def login(request):
    activity_page = None
    cat = None
    if request.method == 'GET':
        activity_page = request.GET.get("activity")
        cat = request.GET.get("category")
        id = request.GET.get("id")
        if not cat:
            cat = m_category.get_category()
    if not activity_page:
        activity_page = m_activity.get_activity_page()
        if not activity_page:
            activity_page = "home"

    data = {
        "activity": activity_page,
        "category": cat,
        "id" : id,
    }
    m_activity.set_activity_page(None)
    return render(request, 'login.html', {"data": data})


@csrf_exempt
def _login_(request):
    activity_page = None
    if request.method == 'GET':
        email = request.GET.get('email')
        password = request.GET.get('pass')
        activity_page = request.GET.get("activity")
        cat = request.GET.get("category")
        id = request.GET.get("id")
        if activity_page == "recipe_list":
            page = recipes.get_recipes_current_page()
            activity_page = "/empty_my_fridge/{0}/?page={1}".format(
                activity_page, page)
        elif (activity_page == "categories" or activity_page == "search") and cat != "None":
            page = m_category.get_category_page()
            activity_page = "/empty_my_fridge/{0}/?category={1}&page={2}".format(
                activity_page, cat, page)
        elif activity_page == "recipe_view_page":
            activity_page = "/empty_my_fridge/{0}/?id={1}".format(activity_page, id)
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
            "msg_type": "success"
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
        friend_id = request.GET.get("id")
        m_user.set_friend_id(friend_id)
        if friend_id:
            pUser = db.child("users").child(friend_id).get().val()
            pUser_details = dict(pUser)
            #pUser._setUser_(user_details)
    data = {
        "user": user_details,
        "pUser": pUser_details
    }
    return render(request, "public_profile.html", {"data": data})

@csrf_exempt
def recipe_view_page(request):
    user = m_user._getUser_()
    uid = m_user._getUser_Id_()
    print_list = []
    recipe_id = request.GET.get("id")
    print(recipe_id)
    link = None
    this_recipe = None
    #"https://firebasestorage.googleapis.com/v0/b/empty-my-fridge-ff73c.appspot.com/o/cutePlate.jpg?alt=media&token=229f016f-e151-4bf7-b569-d6a07a6a2c18"

    if request.method == "POST":
        # recipe_id = request.POST.get("recipe_id")
        # print(recipe_id)
        try:
            file = request.FILES['img']
            _dir_ = "recipe_images/{0}/{1}".format(uid, file.name)
            img_details = fb_storage.child(_dir_).put(file, request.session['token_id'])
            link = fb_storage.child(_dir_).get_url(img_details["downloadTokens"])
        except Exception:
            pass
    if recipe_id:
        recipe_image_update = {
            "recipe_image": link
        }
        this_recipe = db.child("recipe").child(recipe_id).get().val()
        print(this_recipe)
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
        
    
    data = {
        "recipe": this_recipe,
        "ingredients": print_list,
        "recipe_id": recipe_id,
        "user" : user,
    }
    return render(request, 'recipe_view_page.html', {"data": data})


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
        if friends and friends.items() != None:
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
def public_fav_recipes(request):
    if m_user._isNone_():
            return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friend_id = m_user.get_friend_id()
        fav_recipes_list = []
        num_of_fav_recipes = 0
        pUser = None
        if friend_id:
            pUser = db.child("users").child(friend_id).get().val()
            fav_recipes = db.child("user_fav_recipes").child(friend_id).get()
            if fav_recipes.each():
                for recipe in fav_recipes.each():
                    _key_ = str(recipe.key())
                    user_fav_recipe = db.child("recipe").child(_key_).get().val()
                    if user_fav_recipe:
                        recipe_details = dict(user_fav_recipe)
                        recipe_details = recipes.get_recipe(recipe_details, _key_, uid)
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
def public_personal_recipes(request):
    recipe_details = None
    msg = None
    msg_type = None
    userRecipe = None
    no_rec = None
    friend_recipe_list = []

    if m_user._isNone_():
        return HttpResponseRedirect("/empty_my_fridge/login/") 
    else:
        user = m_user._getUser_()
        uid = m_user._getUser_Id_()
        friend_id = m_user.get_friend_id()
        pUser = None
        if friend_id:
            pUser = db.child("users").child(friend_id).get().val()

            my_recipes = db.child("users").child(friend_id).child("recipes").get().each()
            if my_recipes:
                for recipe in my_recipes:
                    recipe_details = recipe.val()
                    if recipe_details["privacy"] != "0":
                        friend_recipe_list.append(recipe_details)   
            else:
                no_rec = "Looks like they don't have any personal recipes at the moment..."
    data = {
        "user": user,
        "pUser": pUser,
        "message": msg,
        "msg_type": msg_type,
        "my_recipes": friend_recipe_list,
        "no_rec": no_rec,
    }
    return render(request, 'public_personal_recipes.html', {"data": data, })


def remove_white_spaces(items):
    new_items = []
    for item in items:
        new_items.append(item.strip().lower())
    return new_items


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
                for person in users.each():
                    person = dict(person.val())
                    if person["email"] == email:
                        thisUser = person
                        break
            elif username:
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
            if accept or deny:
                return HttpResponseRedirect("/empty_my_fridge/friend_requests/")
            #they chose to use userID...
        
        print(friends)
        if friends:
            for key, value in friends.items():
                thisFren = db.child("users").child(key).get().val()
 
                #once you find the right person...
                if not value["added_back"]:
                    friends_list.append(dict(thisFren))
        num_of_friends = len(friends_list)
        
        print(friends_list)
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
def edit_profile(request):
    if m_user._isNone_():
        m_activity.set_activity_page("edit_profile")
        return HttpResponseRedirect("/empty_my_fridge/login/")
    else:
        user = m_user._getUser_()
        data = {
            'user': user,
        }
        return render(request, 'edit_profile.html', {"data": data})


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
                ingredients = remove_white_spaces(ingredients)
                measurements = request.POST.get("measurements").split(",")
                measurements = remove_white_spaces(measurements)
                
                if len(ingredients) == len(measurements):
                    r_key = db.generate_key()
                    description = request.POST.get("description")
                    recipe_categories = request.POST.get("recipe_categories").split(",")
                    recipe_categories = remove_white_spaces(recipe_categories)
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
        admins = db.child("admin").child(
            "UPLwshBH98OmbVivV").child("scrapers").get().val()
        for admin in admins:
            if str(admin) == str(uid):
                isAdmin = True
                break
        data = {
            'user': user_details,
            'admin': isAdmin,
            "msg_type": m_message.get_msg_type(),
            "message": m_message.get_message()
        }
        m_message.set_message(None)
        m_message.set_msg_type(None)
        return render(request, 'account_settings.html', {"data": data})


@csrf_exempt
def reset_password(request):
    data = {
        "msg_type": m_message.get_msg_type(),
        "message": m_message.get_message()
    }
    m_message.set_message(None)
    m_message.set_msg_type(None)
    return render(request, 'reset_password_page.html', {"data": data})


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
        "NOT_VERIFIED": "Your email is not verified! Please, follow the link in your email to verify your account.",
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


@csrf_exempt
def fridge(request):
    uid = None
    if m_user._isNone_():
        activity_page = "/empty_my_fridge/login/?activity=fridge"
        return HttpResponseRedirect(activity_page)
    else:
        uid = m_user._getUser_Id_()
        #user = m_user._getUser_()

    all_ingredients = []
    _all_ingredients_ = db.child("all_ingredients").get().val()
    if(_all_ingredients_):
        for ingredient in _all_ingredients_:
            if ingredient:
                all_ingredients.append(ingredient)
    
    if len(all_ingredients) > 0:
        all_ingredients = sorted(all_ingredients)
    fridge_ingredients = db.child("users").child(uid).child(
        "Fridge").get().val()  # database is cleared of null values
    if fridge_ingredients:
        fridge_ingredients = sorted(fridge_ingredients)

    search_ing = request.GET.get('search_ingredients')

    chk_food = request.POST.getlist('sav_ing')
    del_food = request.POST.getlist('del_ing')
    popup={}
    

    if(request.POST.get('remove_all')):
        db.child("users").child(uid).child("Fridge").remove()
        popup={"all":["Everything"]}
    #all_ingredients = all_ingredients[:50]

    if del_food:
        popup={"del":del_food}
        for food in del_food:
            db.child("users").child(uid).child("Fridge").child(food).remove()

    if search_ing:
        all_ingredients = [i for i in all_ingredients if search_ing in i]
        if not all_ingredients:
            all_ingredients = []
   
    if chk_food and uid:
        new_ingredients = {}
        if fridge_ingredients:
            disj = list(set(chk_food)-set(fridge_ingredients))
            popup={"add":disj}
            for x in disj:
                new_ingredients[x] = x
            db.child("users").child(uid).child(
                "Fridge").update(new_ingredients)

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

    btnclick = request.POST.get('find_Recipe')
    if btnclick:
        return HttpResponseRedirect("/empty_my_fridge/fridge/recipes")
    
    
    context = {
        "ingredients" : all_ingredients, 
        'fing' : fridge_ingredients,
        "user": m_user._getUser_(),
        'fing_amount' : fing_len,
        "popup":popup
         }
    return render(request, 'fridge.html', context )

@csrf_exempt
def fridge_recipes(request):
    if m_user._isNone_():
        activity_page = "/empty_my_fridge/login/?activity=fridge"
        return HttpResponseRedirect(activity_page)

    all_recipes = recipes.get_all_recipes()
    matches = Fridge_matches(all_recipes)
    uid = m_user._getUser_Id_()
    possible_recipes = matches["exact"]
    temp_recipes = []
    if possible_recipes:
        for recipe in possible_recipes:
            try:
                is_fav = recipe["stars"][uid] != None
                recipe["user_saved"] = is_fav
            except KeyError:
                pass
            temp_recipes.append(recipe)
        possible_recipes = temp_recipes
    disp_partial = False
    fridge_recipes = recipes.get_fridge_recipes()
    if request.method == "POST" or fridge_recipes:
        if (request.POST.get('part') == "True" or fridge_recipes == "part"):
            fridge_recipes = "part"
            disp_partial = True
            possible_recipes=[]
            possible_recipes = matches["partial"]
            temp_recipes = []
            if possible_recipes:
                for recipe in possible_recipes:
                    try:
                        is_fav = recipe["stars"][uid] != None
                        recipe["user_saved"] = is_fav
                    except KeyError:
                        pass
                    temp_recipes.append(recipe)
                possible_recipes = temp_recipes
        else:
            disp_partial = False
        recipes.set_fridge_recipes(None)

    if(sorting_type:=request.POST.get('sorting')):
            recipes.set_sorting_type(sorting_type)

    possible_recipes = sort_recipes(possible_recipes, recipes.get_sorting_type()) or possible_recipes

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
        "partial": disp_partial,
        "scrollTop": scrollTop,
        "keep_scroll_pos": keep_scroll_pos,
        "found_results": found_results,
        "items": len(curr_recipes),
        "isSearch": True,
        "fridge_recipes" : fridge_recipes,
        "sorting_type": recipes.get_sorting_type(),
    }

    return render(request, 'fridge_recipes.html', {"data": data})
