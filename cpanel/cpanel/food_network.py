#imports packages  (Be sure to install BeautifulSoup)
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from builtins import any as b_any
import time


#17 Sample recipes for testing (Provided by foodnetwork.com)
recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/food-network-kitchen/applesauce-waffles-3362190', 
'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-with-oil-and-garlic-aglio-et-olio-recipe-1944538', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-cacio-e-pepe-3565584', 
'https://www.foodnetwork.com/recipes/ina-garten/cinnamon-baked-doughnuts-recipe-2135621', 'https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844',
'https://www.foodnetwork.com/recipes/alton-brown/granola-recipe-1939521', 'https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-banana-bread-muffins-recipe-7217371', 
'https://www.foodnetwork.com/recipes/chocolate-lava-cakes-2312421', 'https://www.foodnetwork.com/recipes/ina-garten/garlic-roasted-potatoes-recipe-1913067', 
'https://www.foodnetwork.com/recipes/robert-irvine/french-toast-recipe-1951408','https://www.foodnetwork.com/recipes/food-network-kitchen/curry-fried-rice-recipe-2109760', 'https://www.foodnetwork.com/recipes/ree-drummond/beef-tacos-2632842',
'https://www.foodnetwork.com/recipes/food-network-kitchen/sweet-and-sour-couscous-stuffed-peppers-recipe-2121036','https://www.foodnetwork.com/recipes/dave-lieberman/mexican-chicken-stew-recipe-1917174',
'https://www.foodnetwork.com/recipes/food-network-kitchen/cauliflower-gnocchi-4610559','https://www.foodnetwork.com/recipes/sunny-anderson/easy-chicken-pot-pie-recipe-1923875', 
'https://www.foodnetwork.com/recipes/geoffrey-zakarian/ricotta-gnocchi-2707052', 'https://www.foodnetwork.com/recipes/food-network-kitchen/the-best-cheddar-and-herb-chaffle-8317038', 
'https://www.foodnetwork.com/recipes/ree-drummond/cacio-e-pepe-8640368', 'https://www.foodnetwork.com/recipes/katie-lee/chicken-cauliflower-fried-rice-3588745']

measurementUnits = ['teaspoons','tablespoons','cups','containers','packets','bags','quarts','pounds','cans','bottles',
		'pints','packages','ounces','jars','heads','gallons','drops','envelopes','bars','boxes','pinches',
		'dashes','bunches','recipes','layers','slices','links','bulbs','stalks','squares','sprigs',
		'fillets','pieces','legs','thighs','cubes','granules','strips','trays','leaves','loaves','halves', 'cloves', 'large', 'extra-large', 'small']

modifier = ['dried' , 'freshly', 'chopped', 'with', 'pinch', 'grated','cracked', 'pure', 'extra-large', 'plus', 'silvered', 'cook\'s', 'mashed', 'ripe', 'packed', 'good', 'minced', 'red', 'fajita-sized', 'frozen', 'store', 'bought','medium','drained','few', 'shredded', 'cooked', 'yolk']

#recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240']

#Holds an array of recipe info, the individual array in the grand array is arranged in this order --> [Title, Image, Link to Recipe, Ingredients array]
grand_recipe_list = []


#Parses through the ingredient list 
#Note: Doesn't give description which follow ingredient. (Ex: Peeled, melted, optional, etc)
def parser(item):
	if type(item) != str:
		return
	parsed_word = ''
	split_item = item.split(" ")
	for word in split_item:
		word = word.lower()
		#Takes care of wholenumbers, decimals, and fractions
		if word.isnumeric() or word.isdecimal() or '/' in word:
			continue
		elif b_any(word in x for x in measurementUnits):
			continue
		elif b_any(word in x for x in modifier):
			continue
		elif '(' in word or ')' in word:
			continue
		elif word == 'or':
			break
		elif word == 'and':
			break
		elif ',' in word:
			last_word = word.replace(',','')
			parsed_word = parsed_word + last_word
			break
		else: 
			parsed_word = parsed_word + word + ' '
		
	parsed_word = parsed_word.rstrip()
	return parsed_word


def food_network(db):	
	for recipe in recipes:
		#Array that will hold the info for each individual recipe
		add_to_grand_list = []
		#Website im scraping info on (Default homepage)
		recipe_page = recipe
		#Essentially opening up the connection and downloads the whole html webpage
		uClient = uReq(recipe_page)
		page_html = uClient.read()
		uClient.close()

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
					ingredient_list = parser(item.text, ingredient_list)	
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
			cap+=1
		

	#[Title, Image, Link to Recipe, Ingredients array]
	c = 0;
	for recipe in grand_recipe_list:
		ingredients = recipe[3]
		recipe_name = recipe[0]
		recipe = {
		'recipe_name': recipe_name,
		'recipe_image': recipe[1],
		'recipe_link': recipe[2],
		'recipe_ingredients': ingredients,
		'recipe_categories': recipe[4],
		}
		found = False
		all_recipes = db.child('recipe').get()
		if all_recipes.each() != None:
			for m_recipe in all_recipes.each():
				_recipe_ = 	m_recipe.val()
				if _recipe_["recipe_ingredients"] == ingredients and _recipe_["recipe_name"] == recipe_name:
					found = True
					break
		
		if not found:
			db.child('recipe').push(recipe)		
		
		for ingredient in ingredients:
			_ingredient_ = {
				c : ingredient,
			}
			all_ingredients = db.child("all_ingredients").get().val()
			if all_ingredients != None:
				found = False
				for food_ingredient in all_ingredients:
					if food_ingredient == ingredient:
						found = True
						break
			
			if not found:
				db.child('recipe').push(recipe)
			
			for ingredient in ingredients:
				_ingredient_ = {
					c : ingredient,
				}
				if ingredient and ingredient != "No ingredients" and ingredient != "":
					all_ingredients = db.child("all_ingredients").get().val()
					if all_ingredients != None:
						found = False
						for food_ingredient in all_ingredients:
							if food_ingredient == ingredient:
								found = True
								break	
						if not found:
							db.child('all_ingredients').update(_ingredient_)
							c+=1			
					else:
						db.child('all_ingredients').set(_ingredient_)
						c+=1	
