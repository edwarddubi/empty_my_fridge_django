  
import os
import setuptools
#os.system("pip install Django==3.0.7")
#os.system("pip install pyrebase")
#os.system("pip install beautifulsoup4")
#os.chdir("cpanel")
#os.system("python manage.py runserver")
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='empty_my_fridge',
    version="1.0.2",
    author="Edward Mensah, Becca Boes",
    description="An App to help Get your Daily Recipes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edwarddubi/empty_my_fridge_django",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': [
            'empty_my_fridge=empty_my_fridge.manage:main',
        ],
    },
)