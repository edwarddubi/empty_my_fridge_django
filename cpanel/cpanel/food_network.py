#imports packages  (Be sure to install BeautifulSoup)
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from builtins import any as b_any
import time


#17 Sample recipes for testing (Provided by foodnetwork.com)
# recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/food-network-kitchen/applesauce-waffles-3362190', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-with-oil-and-garlic-aglio-et-olio-recipe-1944538', 'https://www.foodnetwork.com/recipes/food-network-kitchen/spaghetti-cacio-e-pepe-3565584', 'https://www.foodnetwork.com/recipes/ina-garten/cinnamon-baked-doughnuts-recipe-2135621', 'https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844', 'https://www.foodnetwork.com/recipes/alton-brown/granola-recipe-1939521', 'https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-banana-bread-muffins-recipe-7217371', 'https://www.foodnetwork.com/recipes/chocolate-lava-cakes-2312421', 'https://www.foodnetwork.com/recipes/ina-garten/garlic-roasted-potatoes-recipe-1913067', 'https://www.foodnetwork.com/recipes/robert-irvine/french-toast-recipe-1951408','https://www.foodnetwork.com/recipes/food-network-kitchen/curry-fried-rice-recipe-2109760', 'https://www.foodnetwork.com/recipes/ree-drummond/beef-tacos-2632842','https://www.foodnetwork.com/recipes/food-network-kitchen/sweet-and-sour-couscous-stuffed-peppers-recipe-2121036','https://www.foodnetwork.com/recipes/dave-lieberman/mexican-chicken-stew-recipe-1917174','https://www.foodnetwork.com/recipes/food-network-kitchen/cauliflower-gnocchi-4610559','https://www.foodnetwork.com/recipes/sunny-anderson/easy-chicken-pot-pie-recipe-1923875']

#Food Network recipe list from A-Z (Warning: This will take a really long time to scrape)
network_recipes = ['https://www.foodnetwork.com/recipes/recipes-a-z/', 'https://www.foodnetwork.com/recipes/recipes-a-z/a', 'https://www.foodnetwork.com/recipes/recipes-a-z/b', 'https://www.foodnetwork.com/recipes/recipes-a-z/c','https://www.foodnetwork.com/recipes/recipes-a-z/d','https://www.foodnetwork.com/recipes/recipes-a-z/e','https://www.foodnetwork.com/recipes/recipes-a-z/f','https://www.foodnetwork.com/recipes/recipes-a-z/g','https://www.foodnetwork.com/recipes/recipes-a-z/h','https://www.foodnetwork.com/recipes/recipes-a-z/i','https://www.foodnetwork.com/recipes/recipes-a-z/j','https://www.foodnetwork.com/recipes/recipes-a-z/k','https://www.foodnetwork.com/recipes/recipes-a-z/l','https://www.foodnetwork.com/recipes/recipes-a-z/m','https://www.foodnetwork.com/recipes/recipes-a-z/n','https://www.foodnetwork.com/recipes/recipes-a-z/o','https://www.foodnetwork.com/recipes/recipes-a-z/p','https://www.foodnetwork.com/recipes/recipes-a-z/q','https://www.foodnetwork.com/recipes/recipes-a-z/r','https://www.foodnetwork.com/recipes/recipes-a-z/s','https://www.foodnetwork.com/recipes/recipes-a-z/t','https://www.foodnetwork.com/recipes/recipes-a-z/u','https://www.foodnetwork.com/recipes/recipes-a-z/v','https://www.foodnetwork.com/recipes/recipes-a-z/w','https://www.foodnetwork.com/recipes/recipes-a-z/xyz',]

#network_recipes = ['https://www.foodnetwork.com/recipes/recipes-a-z/a']
# list of measurement units for parsing ingredient
measurementUnits = ['teaspoons','tablespoons','cups','containers','packets','bags','quarts','pounds','cans','bottles',
		'pints','packages','ounces','jars','heads','gallons','drops','envelopes','bars','boxes','pinches',
		'dashes','bunches','recipes','layers','slices','links','bulbs','stalks','squares','sprigs',
		'fillets','pieces','legs','thighs','cubes','granules','strips','trays','leaves','loaves','halves', 'cloves', 'large', 'extra-large', 'small', 'grams','milliliters', 'sticks', 'whole', 'handful']

measurementUnitsAbbreviations = ['c', 'c.', 'C','gal', 'oz', 'oz.', 'pt', 'pts', 'pt.', 'lb', 'lb.', 'lbs', 'lbs.', 'Lb', 'Lbs', 'qt', 'qt.', 'qts', 'qts.', 'tbs','tbs.', 'tbsp', 'tbsp.', 'tbspn','tbspn.', 'T', 'T.','tsp','tsp.', 'tspn','tspn.', 't', 't.','g', 'g.', 'kg', 'kg.', 'Kg', 'Kg.', 'l', 'l.', 'L', 'L.', 'mg', 'mg.', 'ml', 'ml.', 'mL', 'mL.', 'pkg', 'pkgs', 'pcs', 'pcs.', ]

# list of adjectives and participles used to describe ingredients
descriptions = ['baked', 'beaten', 'blanched', 'boiled', 'boiling', 'boned', 'breaded', 'brewed', 'broken', 'chilled',
		'chopped', 'cleaned', 'coarse', 'cold', 'cooked', 'cool', 'cooled', 'cored', 'creamed', 'crisp', 'crumbled',
		'crushed', 'cubed', 'cut', 'deboned', 'deseeded', 'diced', 'dissolved', 'divided', 'drained', 'dried', 'dry',
		'fine', 'firm', 'fluid', 'fresh', 'frozen', 'grated', 'grilled', 'ground', 'halved', 'hard', 'hardened',
		'heated', 'heavy', 'juiced', 'julienned', 'jumbo', 'large', 'lean', 'light', 'lukewarm', 'marinated',
		'mashed', 'medium', 'melted', 'minced', 'near', 'opened', 'optional', 'packed', 'peeled', 'pitted', 'popped',
		'pounded', 'prepared', 'pressed', 'pureed', 'quartered', 'refrigerated', 'rinsed', 'ripe', 'roasted',
		'roasted', 'rolled', 'rough', 'scalded', 'scrubbed', 'seasoned', 'seeded', 'segmented', 'separated',
		'shredded', 'sifted', 'skinless', 'sliced', 'slight', 'slivered', 'small', 'soaked', 'soft', 'softened',
		'split', 'squeezed', 'stemmed', 'stewed', 'stiff', 'strained', 'strong', 'thawed', 'thick', 'thin', 'tied', 
		'toasted', 'torn', 'trimmed', 'wrapped', 'vained', 'warm', 'washed', 'weak', 'zested', 'wedged',
		'skinned', 'gutted', 'browned', 'patted', 'raw', 'flaked', 'deveined', 'shelled', 'shucked', 'crumbs',
		'halves', 'squares', 'zest', 'peel', 'uncooked', 'butterflied', 'unwrapped', 'unbaked', 'warmed', 'cracked','good','store', 'bought', 'fajita-sized', 'finely', 'freshly','slow', 'quality', 'sodium', 'mixed', 'wild', 'Asian', 'Italian', 'Chinese', 'American', 'garnished', 'seedless','coarsely', 'natural', 'organic', 'solid']

# list of common ingredients that accidentally get filtered out due to similarities in description list
description_exceptions = ['butter', 'oil', 'cream', 'bread']

# list of numbers as words
numbers = ['one', 'two','three','four','five','six','seven','eight','nine','ten', 'elevin','twelve','dozen']

brands = ['bertolli®', 'cook\'s', 'hothouse', 'NESTLÉ®', 'TOLL HOUSE®']

# misc modifiers (Will sort later)
modifier = ['plus', 'silvered', 'virgin', 'seasoning']

# list of adverbs used before or after description
precedingAdverbs = ['well', 'very', 'super']
succeedingAdverbs = ['diagonally', 'lengthwise', 'overnight']

# list of prepositions used after ingredient name
prepositions = ['as', 'such', 'for', 'with', 'without', 'if', 'about', 'e.g.', 'in', 'into', 'at', 'until', 'won\'t']

# only used as <something> removed, <something> reserved, <x> inches, <x> old, <some> temperature
descriptionsWithPredecessor = ['removed', 'discarded', 'reserved', 'included', 'inch', 'inches', 'old', 'temperature', 'up']

# descriptions that can be removed from ingredient, i.e. candied pineapple chunks
unnecessaryDescriptions = ['chunks', 'pieces', 'rings', 'spears']

# list of prefixes and suffixes that should be hyphenated
hypenatedPrefixes = ['non', 'reduced', 'semi', 'low']
hypenatedSuffixes = ['coated', 'free', 'flavored']	


# recipes = ['https://www.foodnetwork.com/recipes/food-network-kitchen/senate-bean-soup-recipe-1973240', 'https://www.foodnetwork.com/recipes/farfalle-with-herb-marinated-grilled-shrimp-2118008', 'https://www.foodnetwork.com/recipes/farfalle-al-rocco-recipe-1909940', 'https://www.foodnetwork.com/recipes/giada-de-laurentiis/farfalle-with-broccoli-recipe-1945696', 'https://www.foodnetwork.com/recipes/jamie-oliver/farfalle-with-savoy-cabbage-pancetta-thyme-and-mozzarella-recipe2-1909322', 'https://www.foodnetwork.com/recipes/guy-fieri/far-out-farro-salad-recipe-2108223']

#Holds an array of recipe info, the individual array in the grand array is arranged in this order --> [Title, Image, Link to Recipe, Ingredients array]
grand_recipe_list = []


#Parses through the ingredient list 
def parser(item, food_array):
	if type(item) != str:
		return	
	parsed_word = ''

	# Removes unnecessary special characters
	item = item.replace('-', ' ')
	item = item.replace(':', ' ')
	item = item.replace(';', ' ')
	item = item.replace('\'', '')
	item = item.replace('\"', '')
	item = item.replace('%', '')
	item = item.replace('.', '')
	# Breaks each word into a string array
	split_item = item.split(" ")

	for word in split_item:
		word = word.lower()
		#Takes care of wholenumbers, decimals, and fractions
		if word.isnumeric() or word.isdecimal() or '/' in word:
			continue
		elif b_any(word in x for x in description_exceptions):
			parsed_word = parsed_word + ' '
			continue
		elif ',' in word:
			last_word = word.replace(',','')
			parsed_word = parsed_word + last_word
			break
		elif word == 'or':
			break
		elif word == 'and':
			parsed_word = parsed_word.rstrip()
			food_array.append(parsed_word)
			parsed_word = ''
			continue
		elif '(' in word or ')' in word:
			continue
		elif b_any(word in x for x in measurementUnits):
			continue
		elif b_any(word in x for x in measurementUnitsAbbreviations):
			continue
		elif b_any(word in x for x in numbers):
			continue
		elif b_any(word in x for x in brands):
			continue
		elif b_any(word in x for x in descriptions):
			continue
		elif b_any(word in x for x in modifier):
			continue
		elif b_any(word in x for x in precedingAdverbs):
			continue
		elif b_any(word in x for x in succeedingAdverbs):
			continue
		elif b_any(word in x for x in prepositions):
			continue
		elif b_any(word in x for x in descriptionsWithPredecessor):
			continue
		elif b_any(word in x for x in unnecessaryDescriptions):
			continue		
		else: 
			parsed_word = parsed_word + word + ' '
		
	parsed_word = parsed_word.strip()

	#Prevent's blank spots in ingredients array
	if parsed_word == '':
		return food_array
	else:
		food_array.append(parsed_word)
		return food_array


def food_network(db):
	print('Now scraping for recipes!')
	print('For the time being, get yourself a coffee while you wait.')
	print('\n')
	# should be a total of 24 pages
	page_num = 0	
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
			#print(the_recipe)
			
			#Array that will hold the info for each individual recipe
			add_to_grand_list = []
			#Website im scraping info on (Default homepage) 
			#recipe_page = the_recipe
			#Essentially opening up the connection and downloads the whole html webpage
			uClient = uReq(the_recipe)
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
		c = 0
		for recipe in grand_recipe_list:
			#Checks to see if list is empty (Will not inclide recipe_ing)
			if not recipe[3]:
				ingredients = ['No ingredients']
			else:
				ingredients = recipe[3]
			recipe_name = recipe[0]
			recipe = {
			'recipe_name': recipe_name,
			'recipe_image': recipe[1],
			'recipe_link': recipe[2],
			'recipe_ingredients': ingredients,
			'recipe_categories': recipe[4],
			}
			#db.child('recipe').push(recipe)		
			
			found = False
			all_recipes = db.child('recipe').get()
			if all_recipes.each() != None:
				for m_recipe in all_recipes.each():
					_recipe_ = m_recipe.val()
					try:
						if _recipe_["recipe_ingredients"] == ingredients and _recipe_["recipe_name"] == recipe_name:
							found = True
							break
					except KeyError:
						pass	
			
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