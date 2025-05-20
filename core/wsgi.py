"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

env = os.environ.get('DJANGO_ENV', 'dev').lower()
if env == 'prod':
    settings_module = 'core.settings.prod'
elif env == 'test':
    settings_module = 'core.settings.test'
else:
    settings_module = 'core.settings.dev'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
