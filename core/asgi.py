"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

env = os.environ.get('DJANGO_ENV', 'dev').lower()
if env == 'prod':
    settings_module = 'core.settings.prod'
elif env == 'test':
    settings_module = 'core.settings.test'
else:
    settings_module = 'core.settings.dev'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()
