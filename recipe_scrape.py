#imports packages  (Be sure to install BeautifulSoup)
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

numbers = [1,2,3,4,5,6,7,8,9,10]
for num in numbers:
	pass
	#Website im scraping info on (Default homepage)
	allRecipes = 'https://www.allrecipes.com/recipes/?page=' + str(num)
	#Essentially opening up the connection and downloads the whole html webpage
	uClient = uReq(allRecipes)
	page_html = uClient.read()
	uClient.close()

	#Parses the html data (This is where the fun begins)
	page_soup = soup(page_html, "html.parser")


	#Gets area in the website where all the important data is displayed (The area where the recipe cards are in this case)
	recipe_cards = page_soup.findAll("article", {"class":"fixed-recipe-card"})

	#Note: 20 Recipe cards are displayed per page (Sometime 19 due to advertising)
	#Get's all the cards that are displayed on page 
	#articles = recipe_grid[0].findAll("article", {"class":"fixed-recipe-card"})


	card_links = []

	for link in recipe_cards:
	    #getting the link to the specific recipe in each card (<a> tag)
	    card_links.append(link.a.get('href'))
	    #print(link.a.get('href'))

	index = 0
	for link in card_links:
		#Opens the given link to recipe
		uClient = uReq(link)
		page_html = uClient.read()
		uClient.close()
		#Parses the data
		page_soup = soup(page_html, "html.parser")
		#Gets the name of the recipe
		#title = page_soup.find("h1", {"class":"recipe-summary__h1"})
		#Get title of pinterest related recipes
		pin_title = page_soup.find("h1", {"class":"headline heading-content"})
		#Gets all the recipes displayed on the page
		#ingredience = page_soup.findAll("span", {"class":"recipe-ingred_txt added"})
		#Pinterest version
		pin_ingredience = page_soup.findAll("span", {"class": "ingredients-item-name"})

		
		print('----------------------')
		if pin_title != None:
			print(pin_title.text + '\n')

		else:
			# print(pin_title.text)
			print('No Title')

		print('Link to recipe: ' + card_links[index] + '\n')
		index += 1

		if pin_ingredience != None:
			for i, item in enumerate(pin_ingredience):
				thing = item.text.strip()
				print(thing)		
		print('----------------------' + '\n')
 