"""
WSGI config for cpanel project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    import empty_my_fridge.manage
    settings = 'empty_my_fridge.cpanel.settings'
except ModuleNotFoundError:
    settings = 'cpanel.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

application = get_wsgi_application()
