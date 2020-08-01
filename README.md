## Empty My Fridage (Django)

What is empty my Fridge app?:

## Github link

[Empty My Fridge](https://github.com/edwarddubi/empty_my_fridge_django)

## PYPI

[empty-my-fridge 1.0.3](https://pypi.org/project/empty-my-fridge/)

### Install using command
  - pip install empty-my-fridge

### Run app using
  - empty_my_fridge

## Future Considerations
### Login Page
  - There is an issue with the login page's Register button not quite working (6.30.20 @ 3:30 PM)
  
### Registration Confirmation
  - Once a user registers, there isn't (but should be) a way for them to receive visual confirmation that it has been created

### Adding Ingredients to Fridge
  - User feedback suggested that having the "Add to Fridge" and "Remove from Fridge" buttons in between the left-pane available ingredients and right-pane current fridge would be more intuitive than its current layout

### Pesky Browse Dropdown Button
  - Several users have noted trouble getting the button's dropdown options to stay expanded when they attempt to move their mouse from the button to the options. We suspect this is due to oversized margins on the button itself, but will be investigating this in Sprint #2

### Whole-Tile onClick
  - On the homepage, there are tiles for broad categories. When you look through recipes, each recipe is on its own tile. However, you cannot currently click anywhere on the tile, rather you must click on the title or name itself for the onClick to activate. The next sprint will also focus on fixing this to be more convenient for users
## Python FrameWork

- [Django](https://pypi.org/project/Django/)

## Libraries/Tools

[Pyrebase](https://pypi.org/project/Pyrebase/)

[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)

Semantic Ui or fomantic Ui css (currently, Semantic Ui)

## Templates

- HTML, CSS, and JS (Snippets)

## Using Semantic Ui

- Add this to your HTMl file in the head tag. You can ignore the semantic.min.js in the script tag

```html
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css"
/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js"></script>
```

- It should look like this. Remember, this is just an example to help you know where it needs to put in the HTML file

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Sign Up</title>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css"
    />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js"></script>
  </head>
  <body>
    <!--Your semantic UI here. Example below-->
    <button style="margin: 10;" type="submit" class="ui button fluid red">
      Create Account
    </button>
  </body>
</html>
```

- [Implementation? Read from docs](https://semantic-ui.com/elements/)

## Steps

pip install Django==3.0.7

pip install pyrebase

pip install beautifulsoup4

## Get Firebase Database Config file Set up

Create a config file in the cpanel/cpanel folder. Also, make sure you get the snippet for your app's Firebase config object--this is found in your project settings

- [Firebase config object](https://firebase.google.com/docs/web/setup?authuser=0#from-hosting-urls)

For security reasons, you should exclude the config.py module when exporting project into Github (Don't mind this since gitignore does it anyways)

Example:

```py
def myConfig():
  config = {
    'apiKey': "api-key",
    'authDomain': "project-id.firebaseapp.com",
    'databaseURL': "https://project-id.firebaseio.com",
    'projectId': "project-id",
    'storageBucket': "project-id.appspot.com",
    'messagingSenderId': "sender-id",
    'appId': "app-id",
    'measurementId': "G-measurement-id"
  }
  return config
```

## Get the App running for the first time

- python manage.py

## Using Github

Each of us will create their own respective branches apart from MASTER

use command -> git checkout -b < branchName >

- To pull from Github, use: git pull origin < branchName >

### Deploy from local to remote

- git add .
- git commit -m "message that represents your recent changes"
- git push origin < branchName >

### Note:

Refrain from pushing to master. push to your branch and allow the scrum master to review your work before pushing to master

## Deploy App to Google Cloud or Heroku

- We would have to look into this
- [We might need cloud functions to run our server on the hosting site](https://medium.com/firebase-developers/hosting-flask-servers-on-firebase-from-scratch-c97cfb204579)

- If those don't work now, we might consider using heroku

## SetUp file
 - python -m pip install -U wheel twine setuptools
 - python setup.py sdist bdist_wheel 
 - twine upload dist/*

## Personal Contributions
### User Custom Recipes
  - Users can add a custom recipe with an image to our database, and set the privacy to private (only they can see it), friends (their friends can see their personal recipes), or public (anyone can see it)
  - Users can also opt to change the picture of their recipe, or even delete the entire thing if they so wish
  
### Formatted Recipe Page
  - All scraped recipes end up directing to the external site we found it from. However, in the case a user creates their own recipe, and then wants to see their recipe or let other people see it, a populatable format was needed to display that information.
  - Users with proper permissions can see all custom recipes in this format, and if that user owns the recipe, they can also update the picture of it if they so desire!

### Friends
  - Users can send friend requests using another user's email or username to which that other user can accept or deny.
  - If you click on one of your friends, you can also see a public version of their user profile page, with their friends, favorited recipes, as well as any personal recipes they have created that aren't private
