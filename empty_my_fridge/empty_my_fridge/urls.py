"""cpanel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
#app_name = 'empty_my_fridge'
#python manage.py runserver
urlpatterns = [
    path('', views.home, name='homepage'),
    path('fridge/',views.fridge, name='fridge'),
    path('home/', views.home, name='home'),
    path('recipe_list/', views.recipe_list, name='recipes'),
    path('recipe_page/', views.recipe_page, name='recipe_page'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('to_home/', views._login_, name='to_home'),
    path('to_signIn/', views._register_, name='_register_'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('save_profile/', views.save_profile, name='save_profile'),
    path('personal_recipes/', views.personal_recipes, name='personal_recipes'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('recover_password/', views.recover_password, name='recover_password'),
    path('favorite_recipes/', views.user_fav_recipes, name='favorite_recipes'),
    path('fav_recipe_onclick/', views.fav_recipe_onClick, name='fav_recipe_onclick'),
    path('search_and_filter/', views.search, name='search_and_filter'),
    path('scrape_page/', views.scrape_page, name="scrape_page"),
    path('logout/', views._logout_, name='logout'),
    path('categories/', views.category, name='category'),
    path('search/', views.get_recipes_by_category_ingredients, name='search'),
]
