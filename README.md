## Empty My Fridge (Django)

A web application that tells users recipes they can make based on ingredients in their fridge

## Github link

[Empty My Fridge](https://github.com/edwarddubi/empty_my_fridge_django)

## PYPI

[empty-my-fridge 1.1.6](https://pypi.org/project/empty-my-fridge/)

### Install using command
  - pip3 install empty-my-fridge

### Run app using
  - empty_my_fridge

## Python FrameWork

- [Django](https://pypi.org/project/Django/)

## Libraries/Tools

[Pyrebase](https://pypi.org/project/Pyrebase/)

[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)

Semantic Ui or fomantic Ui css (currently, Semantic Ui)

## Templates

- HTML, CSS, and JS (Snippets)

## Contributions

### Edward Mensah
1. **User Authentication** ***June 6 - June 10***
    - Login/Register/Reset Password
    - Email verification/Logout
2. **User Profile**  ***June 11***
    - View and Edit user information/Account Settings
    - User favorite recipes
    - Change user avatar
3. **Page Routing** ***June 2 - June 11***
    - Navigation bar 
    - Navigating from one page to another
4. **Recipe Page**  ***June 10 - June 20***
    - Get all recipes
    - Ability to populate these recipes on the recipe page
5. **Search** ***June 17***
    - Ability to search for recipes by name
6. **Likes** ***June 12 - June 17***
    - Ability to add a recipe to user's favorites
7. **Packacking** ***June 26 - June 29***
    - Packaged our app and deployed to Pypi
   
### Cyan Perez
1. **User Custom Recipes** ***June 12 - June 24***
    - Users can add a custom recipe with an image to our database, and set the privacy to private (only they can see it) 
    - friends (their friends can see their personal recipes), or public (anyone can see it)
    - Users can also opt to change the picture of their recipe, or even delete the entire thing if they so wish
2. **Formatted User Recipe Page** ***July 18 - July 25***
    - Design and implementation of custom recipe pages
    - Customization of personal recipes' images 
    - Public access to custom recipe pages 
3. **Friends** ***July 18 - July 30***
    - Users have the abilty to send/receive friend requests by id or email
    - Accept/ deny friend requests
    - Delete friends
    - View friends' profile, their firends, favorite recipes, and personal recipes they have permision to view
    
### Rebecca Boes
1. **Home Page** ***June 12 - June 18***
    - Ability to choose from preset categories to view recipes
    - Search bar to find recipes by their categories or ingredients
2. **Categories Page** ***June 20 - June 24***
    - Gets all recipes and populates the page by specified category
    - Accessible through homepage choices and navigation bar dropdown
3. **Recipe Page**  ***June 10 - June 20***
    - Get all recipes
    - Ability to populate these recipes on the recipe page
4. **Pagination** ***June 13 - June 17***
    - Appears on all pages that display recipes
5. **Recipe Filtering** ***July 24 - July 30***
    - Ability for users to filter recipes both on recipes and categories pages
    - Saves current choices so users can add or remove as needed
    - Choice to either show exact matches for all applied filters or show all recipes that match at least one filter
6. **Packacking** ***June 26 - June 29***
    - Packaged our app and deployed to Pypi
   
### Charles Charlestin III
  1. **Web Scraping** ***June 9 - July 29***
      - Utilized the beautiful soup python library to perform web scraping on desired webpages
        - Uses recipe data from allrecipes.com
        - Previously used recipe data from foodnetwork.com(Discontinued from sprint 1)
      - Populate databes with recipe information such as: title, image, address, ingredients, and categories
      - Admins of Empty_My_Fridge can choose to scrape from thousands of recipe pages available and add the data to the database

  2. **Ingredient Parsing** ***June 9 - July 29***
      - Parsed the obtained ingredient data to be utilized for the "My Fridge" Page
      - Originally used a C++ library to parse recipe data for speed     (Discontinued from spring 1)
      - Uses python to parse recipe data with increased accuracy and reliability 

 ### Randolph Maynes
  1. **My Fridge** ***June 17 - July 25***
      - Add/ Remove recipes to user fridge 
      - Filter recipes by ingredients in user fridge
      - Finding partial recipes matches based on ingredients
  2. **Sorting** ***June 28 - July 28***
      - Sort all pages by name, popularity, missing ingredients 
