## Empty My Fridage (Django)

What is empty my Fridge app?:

## Python FrameWork

- Django

## Libraries/Tools

Pyrebase

BeautifulSoup

Semantic Ui or fomantic Ui css (currently, Semantic Ui)

Validate Email

Py3DNS

## Templates

- HTML, CSS, and JS

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

pip install validate_email

pip install py3DNS

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

- python manage.py runserver

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
