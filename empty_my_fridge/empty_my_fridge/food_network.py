#imports packages  (Be sure to install BeautifulSoup)
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from builtins import any as b_any
from ctypes import *
import time
import os
import sys, select


#17 Sample recipes for testing (Provided by foodnetwork.com)
# recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/food-network-kitchen/applesauce-waffles-3362190', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-with-oil-and-garlic-aglio-et-olio-recipe-1944538', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-cacio-e-pepe-3565584', 'https://www.foodnetwork.com/recipes/ina-garten/cinnamon-baked-doughnuts-recipe-2135621', 'https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844', 'https://www.foodnetwork.com/recipes/alton-brown/granola-recipe-1939521', 'https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-banana-bread-muffins-recipe-7217371', 'https://www.foodnetwork.com/recipes/chocolate-lava-cakes-2312421', 'https://www.foodnetwork.com/recipes/ina-garten/garlic-roasted-potatoes-recipe-1913067', 'https://www.foodnetwork.com/recipes/robert-irvine/french-toast-recipe-1951408','https://www.foodnetwork.com/recipes/food-network-kitchen/curry-fried-rice-recipe-2109760', 'https://www.foodnetwork.com/recipes/ree-drummond/beef-tacos-2632842','https://www.foodnetwork.com/recipes/food-network-kitchen/sweet-and-sour-couscous-stuffed-peppers-recipe-2121036','https://www.foodnetwork.com/recipes/dave-lieberman/mexican-chicken-stew-recipe-1917174','https://www.foodnetwork.com/recipes/food-network-kitchen/cauliflower-gnocchi-4610559','https://www.foodnetwork.com/recipes/sunny-anderson/easy-chicken-pot-pie-recipe-1923875']

#Food Network recipe list from A-Z (Warning: This will take a really long time to scrape)
network_recipes = ['https://www.foodnetwork.com/recipes/recipes-a-z/', 'https://www.foodnetwork.com/recipes/recipes-a-z/a', 'https://www.foodnetwork.com/recipes/recipes-a-z/b', 'https://www.foodnetwork.com/recipes/recipes-a-z/c','https://www.foodnetwork.com/recipes/recipes-a-z/d','https://www.foodnetwork.com/recipes/recipes-a-z/e','https://www.foodnetwork.com/recipes/recipes-a-z/f','https://www.foodnetwork.com/recipes/recipes-a-z/g','https://www.foodnetwork.com/recipes/recipes-a-z/h','https://www.foodnetwork.com/recipes/recipes-a-z/i','https://www.foodnetwork.com/recipes/recipes-a-z/j','https://www.foodnetwork.com/recipes/recipes-a-z/k','https://www.foodnetwork.com/recipes/recipes-a-z/l','https://www.foodnetwork.com/recipes/recipes-a-z/m','https://www.foodnetwork.com/recipes/recipes-a-z/n','https://www.foodnetwork.com/recipes/recipes-a-z/o','https://www.foodnetwork.com/recipes/recipes-a-z/p','https://www.foodnetwork.com/recipes/recipes-a-z/q','https://www.foodnetwork.com/recipes/recipes-a-z/r','https://www.foodnetwork.com/recipes/recipes-a-z/s','https://www.foodnetwork.com/recipes/recipes-a-z/t','https://www.foodnetwork.com/recipes/recipes-a-z/u','https://www.foodnetwork.com/recipes/recipes-a-z/v','https://www.foodnetwork.com/recipes/recipes-a-z/w','https://www.foodnetwork.com/recipes/recipes-a-z/xyz',]

#network_recipes = ['https://www.foodnetwork.com/recipes/recipes-a-z/b']

# recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/farfalle-with-herb-marinated-grilled-shrimp-2118008', 'https://www.foodnetwork.com/recipes/farfalle-al-rocco-recipe-1909940', 'https://www.foodnetwork.com/recipes/giada-de-laurentiis/farfalle-with-broccoli-recipe-1945696', 'https://www.foodnetwork.com/recipes/jamie-oliver/farfalle-with-savoy-cabbage-pancetta-thyme-and-mozzarella-recipe2-1909322', 'https://www.foodnetwork.com/recipes/guy-fieri/far-out-farro-salad-recipe-2108223']

app_path = os.path.abspath(__file__)
app_path = os.path.realpath(app_path)
app_path = os.path.dirname(app_path)

if os.name == "nt":
	app_path = os.path.join(app_path, "recipe_parsing.dll")
	lib = CDLL(app_path)
else:
	app_path = os.path.join(app_path, "librecipe_parsing.so")
	lib = CDLL(app_path)

lib.parser.restype = c_char_p
lib.parser.argtype = c_char_p

#Parses through the ingredient list
def minor_parsing(food):
	food = str(food)
	food = food[1:]
	food = food.replace('\xc2\xa0','')
	food = food.replace('\'', '')
	food = food.strip()
	return food


def food_network(db):
	print('Getting all recipes in database. Please wait....')
	
	# should be a total of 24 pages
	page_num = 0
	all_recipes = db.child('recipe').get().each()
	"""
	_all_recipes_ = []
	if _all_recipes_.each() != None:
		for m_recipe in _all_recipes_.each():
			_recipe_ = m_recipe.val()
	"""
			
	
	print('Done!')
	print('\n')		
	print('Now scraping for recipes!')
	print('For the time being, get yourself a coffee while you wait.')
	print('\n')
	
	#Holds an array of recipe info, the individual array in the grand array is arranged in this order --> [Title, Image, Link to Recipe, Ingredients array]
	grand_recipe_list = []
	for page_link in network_recipes:
		print('Now scraping page ' + str(page_num) + ' out of 24' )
		page_num = page_num + 1
		# ---------- ---------- Scraping Page With All Recipe Links---------- ----------
		recipe_link = page_link
		uClient = uReq(recipe_link)
		page_html = uClient.read()
		uClient.close()
		page_soup = soup(page_html, "html.parser")
		recipes = page_soup.findAll('li', {"class":"m-PromoList__a-ListItem"})

		cap = 0
		# ---------- ---------- Scraping Each Recipe Link In Page---------- ----------
		for recipe in recipes:
			if cap == 10:
				break
			the_recipe = str(recipe.find('a')['href'])
			the_recipe = the_recipe.replace('//', '')
			the_recipe = 'https://' + the_recipe
			print(the_recipe)
			
			
			#Website im scraping info on (Default homepage) 
			#recipe_page = the_recipe
			#Essentially opening up the connection and downloads the whole html webpage
			uClient = uReq(the_recipe)
			page_html = uClient.read()
			uClient.close()

			#Array that will hold the info for each individual recipe
			add_to_grand_list = []

			#Parses the html data (This is where the fun begins)
			page_soup = soup(page_html, "html.parser")

			#gets relavent html info
			recipe_title = page_soup.find("span", {"class":"o-AssetTitle__a-HeadlineText"})
			recipe_img = page_soup.find("img", {"class":"m-MediaBlock__a-Image a-Image"})
			recipe_ingredients = page_soup.findAll("p", {"class":"o-Ingredients__a-Ingredient"})
			recipe_cat = page_soup.findAll('a', {"class":"o-Capsule__a-Tag a-Tag"})

			
			# ---------- ---------- Getting Title ---------- ----------
			if recipe_title != None:
				add_to_grand_list.append(recipe_title.text)
			else:
				add_to_grand_list.append('No Title')
			
			# ---------- ---------- Getting Image Source ---------- ----------
			if recipe_img.get("src") != None:
				add_to_grand_list.append(str(recipe_img.get("src")))
			else:
				add_to_grand_list.append('https://cdn.dribbble.com/users/1012566/screenshots/4187820/topic-2.jpg')
			# ---------- ---------- Getting Recipe Source ---------- ----------
			add_to_grand_list.append(the_recipe)
			
			# ---------- ---------- Getting Ingredients ---------- ----------
			ingredient_list = []
			if recipe_ingredients != None:
				for item in recipe_ingredients:			
					bite = bytes(item.text, 'utf-8')
					food = lib.parser(bite)
					food = minor_parsing(food)
					#print(item.text)
					#print(food)
					ingredient_list.append(food)
			add_to_grand_list.append(ingredient_list)

			
			# ---------- ---------- Getting Recipe Categories ---------- ----------
			category_list = []
			if recipe_cat != None:
				for cat in recipe_cat:
					#print(cat.text)
					category_list.append(cat.text.lower())
			add_to_grand_list.append(category_list)

			grand_recipe_list.append(add_to_grand_list)

			#Used to have a 1 second delay for each recipe scraped. Helps prevents forced connection drops from host
			time.sleep(1)
			cap += 1
			
		if page_num % 5 == 0:
			prompt = 'Idle: Scraping paused...\n{0} recipes have been scraped.\n*Note: If you continue with no, scraped recipes would be populated in database\nResume scraping? y/N: '.format((page_num - 1) * 10)
			c = input(prompt)
			if c.lower() == 'n':
				print("Stopping...Please wait...")
				break;
		
	
	#[Title, Image, Link to Recipe, Ingredients array]
	print("Populating database. please wait...")
	all_categories = []
	_all_ingredients_ = []
	
	for recipe in grand_recipe_list:
		#Checks to see if list is empty (Will not inclide recipe_ing)
		if not recipe[3]:
			ingredients = ['No ingredients']
		else:
			ingredients = recipe[3]
		recipe_name = recipe[0]
		categories = recipe[4]
		recipe = {
		'recipe_name': recipe_name,
		'recipe_image': recipe[1],
		'recipe_link': recipe[2],
		'recipe_ingredients': ingredients,
		'recipe_categories': categories,
		}		
		
		found = False
		_all_ingredients_ = list(dict.fromkeys(_all_ingredients_ + ingredients))
		all_categories = list(dict.fromkeys(all_categories + categories))
		
		if all_recipes != None:
			for m_recipe in all_recipes:
				_recipe_ = m_recipe.val()
				try:
					if _recipe_["recipe_ingredients"] == ingredients and _recipe_["recipe_name"] == recipe_name:
						found = True
						break
				except KeyError:
					pass	
		
		if not found:
			db.child('recipe').push(recipe)
				
	
	db.child('all_ingredients').set(_all_ingredients_)
	db.child('all_categories').set(all_categories)
	print("Done!\nDb has been populated with new data")
				