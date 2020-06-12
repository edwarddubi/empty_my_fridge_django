#imports packages  (Be sure to install BeautifulSoup)
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from builtins import any as b_any
import pyrebase
from . import config
import time

firebase = pyrebase.initialize_app(config.myConfig())
db = firebase.database()


#17 Sample recipes for testing (Provided by foodnetwork.com)
recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/food-network-kitchen/applesauce-waffles-3362190', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-with-oil-and-garlic-aglio-et-olio-recipe-1944538', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-cacio-e-pepe-3565584', 'https://www.foodnetwork.com/recipes/ina-garten/cinnamon-baked-doughnuts-recipe-2135621', 'https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844', 'https://www.foodnetwork.com/recipes/alton-brown/granola-recipe-1939521', 'https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-banana-bread-muffins-recipe-7217371', 'https://www.foodnetwork.com/recipes/chocolate-lava-cakes-2312421', 'https://www.foodnetwork.com/recipes/ina-garten/garlic-roasted-potatoes-recipe-1913067', 'https://www.foodnetwork.com/recipes/robert-irvine/french-toast-recipe-1951408','https://www.foodnetwork.com/recipes/food-network-kitchen/curry-fried-rice-recipe-2109760', 'https://www.foodnetwork.com/recipes/ree-drummond/beef-tacos-2632842','https://www.foodnetwork.com/recipes/food-network-kitchen/sweet-and-sour-couscous-stuffed-peppers-recipe-2121036','https://www.foodnetwork.com/recipes/dave-lieberman/mexican-chicken-stew-recipe-1917174','https://www.foodnetwork.com/recipes/food-network-kitchen/cauliflower-gnocchi-4610559','https://www.foodnetwork.com/recipes/sunny-anderson/easy-chicken-pot-pie-recipe-1923875']

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
"""
print('Now scraping for recipes!')
print('For the time being, get yourself a coffee while you wait.')
print('\n')
"""
def food_network():	
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

			
		if recipe_title != None:
			add_to_grand_list.append(recipe_title.text)
		else:
			add_to_grand_list.append('No Title')

		if recipe_img != None:
			add_to_grand_list.append(str(recipe_img.get("src")))
		else:
			add_to_grand_list.append('No Image')

		#add link to recipe to array
		add_to_grand_list.append(recipe)

		ingredient_list = []
		index = 0
		if recipe_ingredients != None:
			for item in recipe_ingredients:
				#print(item.text)
				parsed_item = parser(item.text)	
				ingredient_list.append(parsed_item)
		else:
			print('No ingredients')

		add_to_grand_list.append(ingredient_list)
		grand_recipe_list.append(add_to_grand_list)
		#Used to have a 1 second delay for each recipe scraped. Helps prevents forced connection drops from host
		time.sleep(1)
		



	#[Title, Image, Link to Recipe, Ingredients array]
	for recipe in grand_recipe_list:
		recipe = {
		'recipe_name': recipe[0],
		'recipe_image': recipe[1],
		'recipe_link': recipe[2],
		'recipe_ingredients': recipe[3]
		}
		db.child('recipe').push(recipe)
		"""
		print('Recipe name: ' + recipe[0])
		print('Recipe image: '+ recipe[1])
		print('Link to recipe ' + str(recipe[2]))
		print('List of ingredients')
		print('----------------------')
		
 
		for ingredient in recipe[3]:
			food = {
				'food_name': ingredient
			}
			#db.child('food').push(food)
			#print(ingredient)
		"""
		#print('\n')