from .base import *
import secrets

# Impostazioni hardcoded per test
DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
SECRET_KEY = secrets.token_urlsafe(50)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Aggiungi qui eventuali app di test
INSTALLED_APPS += [
    # 'nome_app_test',
]

# Override static/media per test
STATIC_ROOT = '/tmp/test_staticfiles'
MEDIA_ROOT = '/tmp/test_media'
