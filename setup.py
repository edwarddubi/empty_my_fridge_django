import os
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='empty_my_fridge',
    version="1.1.4",
    author="Charles Charlestin, Rebecca Boes, Cyan Perez, Randolph Maynes, Edward Mensah",
    description="Get your Daily Recipes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edwarddubi/empty_my_fridge_django",
    packages=setuptools.find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data = True,
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': [
            'empty_my_fridge=empty_my_fridge.manage:main',
        ],
    },
)