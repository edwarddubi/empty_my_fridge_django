## Empty My Fridage (Django)

What is empty my Fridge app?:

## Libraries
Pyrebase

Django

Semantic Ui with fomantic css (finding a way to add this)

## Steps
pip install Django==3.0.7

pip install pyrebase


## Get Firebase Database Config File SetUp
Create a config file and import into firebaseDb

For security reasons you should exclude when exporting project into Github

Example:

```py
def myConfig():
  config = {
    'apiKey': "",
    'authDomain': "empty-my-fridge.firebaseapp.com",
    'databaseURL': "https://empty-my-fridge.firebaseio.com",
    'projectId': "empty-my-fridge",
    'storageBucket': "",
    'messagingSenderId': "",
    'appId': "",
    'measurementId': ""
  }
  return config
  ```

## Get the App running for the first time
- python manage.py runserver

## Using Github
Each of us will create their own respective branches apart from MASTER

use command -> git checkout -b  < branchName >

### Deploy from local to remote

*git add .

*git commit -m "message that represents your recent changes"

*git push origin < branchName > 
  
### Note: 
Refrain from pushing to master. push to your branch and allow the scrum master to review your work before pushing to master

## Deploy App to Firebase Hosting
*We would have to look into this

*Read more from here [https://medium.com/swlh/how-to-deploy-a-react-app-with-firebase-hosting-98063c5bf425]

*We might need cloud functions to run our server on the hosting site [https://medium.com/firebase-developers/hosting-flask-servers-on-firebase-from-scratch-c97cfb204579]

*If those don't work now, we might consider using heroku
