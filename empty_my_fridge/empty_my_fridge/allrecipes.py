from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from builtins import any as b_any
import time
import unicodedata

# list of measurement units for parsing ingredient
measurementUnits = ['teaspoons','tablespoons','cups','containers','packets','bags','quarts','pounds','cans','bottles',
		'pints','packages','ounces','jars','heads','gallons','drops','envelopes','bars','boxes','pinches',
		'dashes','bunches','recipes','layers','slices','links','bulbs','stalks','squares','sprigs',
		'fillets','pieces','legs','thighs','cubes','granules','strips','trays','leaves','loaves','halves', 'cloves', 'large', 
		'extra-large', 'small', 'grams','milliliters', 'sticks', 'whole', 'handful', 'unsalted', 'salted', 'baby']

measurementUnitsAbbreviations = ['c', 'c.', 'C','gal', 'oz', 'oz.', 'pt', 'pts', 'pt.', 'lb', 'lb.', 'lbs', 'lbs.', 'Lb', 'Lbs', 'qt', 
		'qt.', 'qts', 'qts.', 'tbs','tbs.', 'tbsp', 'tbsp.', 'tbspn','tbspn.', 'T', 'T.','tsp','tsp.', 'tspn','tspn.', 't', 't.','g', 'g.', 'kg', 'kg.', 
		'Kg', 'Kg.', 'l', 'l.', 'L', 'L.', 'mg', 'mg.', 'ml', 'ml.', 'mL', 'mL.', 'pkg', 'pkgs', 'pcs', 'pcs.', ]

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
		'halves', 'squares', 'zest', 'peel', 'uncooked', 'butterflied', 'unwrapped', 'unbaked', 'warmed', 'cracked','good','store', 
		'bought', 'fajita-sized', 'finely', 'freshly','slow', 'quality', 'sodium', 'mixed', 'wild', 'French', 'African' ,'Mexican','Asian', 'Italian', 'Chinese', 'American', 
		'garnished', 'seedless','coarsely', 'natural', 'organic', 'solid','solid', 'heaping','stoned', 'homemade', 'canned', 'unsweetened', 'instant']

# list of common ingredients that accidentally get filtered out due to similarities in description list
description_exceptions = ['butter', 'oil', 'cream', 'bread','all', 'salt']

nonplurals = ['eggs', 'sugars']
# list of numbers as words
numbers = ['one', 'two','three','four','five','six','seven','eight','nine','ten', 'elevin','twelve','dozen']

brands = ['bertolli®', 'cook\'s', 'hothouse', 'NESTLÉ®', 'TOLL HOUSE®']

# misc modifiers (Will sort later)
modifier = ['plus', 'silvered', 'virgin', 'seasoning', 'taste', 'yolk', 'meat', 'frying']

# list of adverbs used before or after description
precedingAdverbs = ['well', 'very', 'super']
succeedingAdverbs = ['diagonally', 'lengthwise', 'overnight']

# list of prepositions used after ingredient name
prepositions = ['as', 'such', 'for', 'with', 'without', 'if', 'about', 'e.g.', 'in', 'into', 'at', 'until', 'won\'t']

# only used as <something> removed, <something> reserved, <x> inches, <x> old, <some> temperature
descriptionsWithPredecessor = ['removed', 'discarded', 'reserved', 'included', 'inch', 'inches', 'old', 'temperature', 'up']

# descriptions that can be removed from ingredient, i.e. candied pineapple chunks
unnecessaryDescriptions = ['chunks', 'pieces', 'rings', 'spears', 'style', 'desserts']

# list of prefixes and suffixes that should be hyphenated
hypenatedPrefixes = ['non', 'reduced', 'semi', 'low']
hypenatedSuffixes = ['coated', 'free', 'flavored']

vulgarFractions = ['¼','½','¾','⅐','⅑','⅒','⅓','⅔','⅕','⅖','⅗','⅘','⅙','⅚','⅛','⅜','⅝','⅞','⅟']

nonplurals = ['eggs', 'sugars', 'onions']
def parser(ingredient, food_array):
	if type(ingredient) != str:
	   return 	
	
	parsed_word = ''
	
	# Removes unnecessary special characters
	ingredient = ingredient.strip()
	ingredient = ingredient.replace('-', ' ')
	ingredient = ingredient.replace(':', ' ')
	ingredient = ingredient.replace(';', ' ')
	ingredient = ingredient.replace('/', ' ')
	ingredient = ingredient.replace('\'', ' ')
	ingredient = ingredient.replace('\"', ' ')
	ingredient = ingredient.replace('%', ' ')
	ingredient = ingredient.replace('.', ' ')
	ingredient = ingredient.replace('&', ' ')
	ingredient = ingredient.replace('[', ' ')
	ingredient = ingredient.replace(']', ' ')
	ingredient = ingredient.replace('®', '')
	ingredient = ingredient.replace('\u2009',' ')
	# Breaks each word into a string array
	split_item = ingredient.split(" ")
	# print(split_item)
	for word in split_item:
		word = word.lower()
		#Takes care of wholenumbers, decimals, and fractions
		if word.isnumeric() or word.isdecimal():
			continue
		elif b_any(word in x for x in description_exceptions):
			parsed_word = word + ' '
			continue
		elif word in nonplurals:
			word = word[:-1]
			parsed_word = parsed_word + word + ' '
			continue	
		elif ',' in word:
			last_word = word.replace(',','')
			if last_word in nonplurals:
				last_word = last_word[:-1]
			parsed_word = parsed_word + last_word
			break
		elif word == 'or':
			break
		elif word == 'and':
			parsed_word = parsed_word.rstrip()
			# food_array.append(parsed_word)
			parsed_word = ''
			continue
		elif '(' in word or ')' in word:
			continue
		elif b_any(word in x for x in vulgarFractions):
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
		elif b_any(word in x for x in hypenatedPrefixes):
			continue	
		elif b_any(word in x for x in hypenatedSuffixes):
			continue			
		else: 
			parsed_word = parsed_word + word + ' '
	
	parsed_word = parsed_word.strip()
	#return parsed_word
	#print(parsed_word)
	#Prevent's blank spots in ingredients array
	if parsed_word == '':
		return food_array
	else:
		food_array.append(parsed_word)
		return food_array
	
	
def allrecipes(db):
	menu = "Stop scraping after...page numbers completed.\n1. 3 pages\n2. 5 pages\n3. All pages\n4. Custom\nOption: "
	option = input(menu)
	if option == "1":
		page_num = 3
	elif option == "2":
		page_num = 5
	elif option == "3":
		page_num = len(numbers) + 1
	elif option == "4":
		page_num = input("Custom: ")
		page_num = int(page_num)

	print('Getting all ingredients in database. Please wait....')
	
	_all_ingredients_ = db.child("all_ingredients").get().val()
	print('Done!')
	print('\n')	
	#Array that will hold the info for each individual recipe
	grand_recipe_list = [] 
	print('Now scraping for recipes!')
	print('For the time being, get yourself a coffee while you wait.')
	print('\n')

	num = 0
	while num < 15:
		print('Now scraping page ' + str(num) + ' out of ' + str(len(numbers) + 1))
		# ---------- ---------- Scraping Page With All Recipe Links---------- ----------
		allrecipe = 'https://www.allrecipes.com/recipes/?page=' + str(num)
		uClient = uReq(allrecipe)
		page_html = uClient.read()
		uClient.close()
		page_soup = soup(page_html, "html.parser")
		recipe_cards = page_soup.findAll('article', {"class":"fixed-recipe-card"}) #The area where the recipe cards are
		num = num + 1
		# ---------- ---------- Scraping Each Recipe Link In Page---------- ----------
		for recipe in recipe_cards:
			#Array Layout order as follows: [Title, Image, Link to Recipe, Ingredients, Categories]
			add_to_grand_list = []   
			
			recipe_link = recipe.a.get('href')
			uClient = uReq(recipe_link)
			page_html = uClient.read()
			uClient.close()
			page_soup = soup(page_html, "html.parser")
			
			#gets relavent html info (2 sets of html elements due to having a modern and legacy page layout options)
			
			if page_soup.find("h1", {"class":"headline heading-content"}) != None:
				recipe_title = page_soup.find("h1", {"class":"headline heading-content"})
			else:
				recipe_title = page_soup.find("h1", {"class":"recipe-summary__h1"})

			if page_soup.find("div", {"class":"image-container"}) != None:
				recipe_img = page_soup.find("div", {"class":"image-container"})
			else:
				recipe_img = page_soup.find("img", {"class":"rec-photo"})

			if page_soup.findAll("span", {"class":"ingredients-item-name"}) != []:
				recipe_ingredients = page_soup.findAll("span", {"class":"ingredients-item-name"})
			else:
				recipe_ingredients = page_soup.findAll("span", {"class":"recipe-ingred_txt added"})

			if page_soup.findAll('span', {"class":"breadcrumbs__title"}) != []:
				recipe_cat = page_soup.findAll('span', {"class":"breadcrumbs__title"})
			else:
				# recipe_cat = page_soup.findAll('meta', itemprop="recipeCategory") Gets categories from meta data, may use later
				recipe_cat = page_soup.findAll('span', {"class": "toggle-similar__title"})

			# ---------- ---------- Getting Title ---------- ----------
			if recipe_title != None:
				add_to_grand_list.append(recipe_title.text)
			else:
				add_to_grand_list.append('No Title Avaliable')

			# ---------- ---------- Getting Image Source ---------- ----------
			if recipe_img.div != None:
				add_to_grand_list.append(recipe_img.div['data-src']) #Image from modern page
			elif recipe_img != None:
				add_to_grand_list.append(recipe_img['src']) # Image from legacy page
			else:
				add_to_grand_list.append('https://cdn.dribbble.com/users/1012566/screenshots/4187820/topic-2.jpg') # Placeholder image if no image is avaliable

			# ---------- ---------- Getting Recipe Source ---------- ----------
			add_to_grand_list.append(recipe_link)
			print(recipe_link)
			# ---------- ---------- Getting Ingredients ---------- ----------
			ingredient_list = []
			if recipe_ingredients != None:
				for ingredient in recipe_ingredients:			
					ingredient_list = parser(ingredient.text, ingredient_list)
			add_to_grand_list.append(ingredient_list)

			
			# ---------- ---------- Getting Recipe Categories ---------- ----------
			category_list = []
			if recipe_cat != None:
				recipe_script_pin = page_soup.find("script", {"id":"karma-loader"})
				recipe_script_legacy = page_soup.find_all("script")

				if recipe_script_pin != None:
					step_0 = str(recipe_script_pin)
					step_1 = step_0.split('tags: [')
					step_2 = " ".join(step_1[1].split())
					step_3 = step_2.split(']')[0].strip()
					step_4 = step_3.replace('"', '')
					step_5 = step_4.split(',')
					for category in step_5:
						category = category.strip()
						category_list.append(category.lower())
				elif recipe_script_legacy != None:
					try:
						step_0 = str(recipe_script_legacy[30])
						step_1 = step_0.split('var RdpInferredTastePrefs = [')
						step_2 = " ".join(step_1[1].split())
						step_3 = step_2.split(']')[0].strip()
						step_4 = step_3.replace('"', '')
						step_5 = step_4.split(',')
						for category in step_5:
							category = category.strip()
							category_list.append(category.lower())
					except IndexError:
						category_list.append("None")
						pass
				else:	
					for category in recipe_cat:
						category = category.text.strip()
						if category == 'Home': # Not a category
							continue
						elif category == 'Chevron Right': # Weird '<' character
							continue
						elif category == 'Recipes': # Not a category
							continue
						else:
							category_list.append(category.lower())
			add_to_grand_list.append(category_list)

			grand_recipe_list.append(add_to_grand_list)
			#Used to have a 1 second delay for each recipe scraped. Helps prevents forced connection drops from host
			time.sleep(1)
		
		res = '{0} recipes have been scraped.\nStopping...Please wait...'.format((num - 1) * 21)
		if page_num == num - 1:
			print(res)
			break
			


	#[Title, Image, Link to Recipe, Ingredients array]
	print("Populating database. please wait...")
	if not _all_ingredients_:
		_all_ingredients_ = []
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

		#if ingredients not in _all_ingredients_:
		_all_ingredients_ = list(dict.fromkeys(_all_ingredients_ + ingredients))
		all_recipes = db.child('recipe').get().each()
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
	print("Done!\nDb has been populated with new data")	
