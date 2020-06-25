import os

os.system("pip install Django==3.0.7")
os.system("pip install pyrebase")
os.system("pip install bs4")
os.system("pip install py3-validate_email")
os.system("pip install dnspython")
os.chdir("cpanel")
os.system("python manage.py runserver") 