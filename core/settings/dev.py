from .base import *
import secrets

# Impostazioni hardcoded per sviluppo
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

try:
    from django.contrib.sites.models import Site
    site_host = Site.objects.get(id=SITE_ID).domain
    if site_host and site_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(site_host)
except Exception:
    pass

SECRET_KEY = secrets.token_urlsafe(50)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Aggiungi qui eventuali app di sviluppo
INSTALLED_APPS += [
    # 'nome_app_sviluppo',
]

CUPS_HOST = os.getenv("CUPS_HOST", "localhost")
CUPS_PORT = os.getenv("CUPS_PORT", "631")