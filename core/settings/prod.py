from .base import *
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env nella root del progetto
load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')

if ALLOWED_HOSTS:
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')
else:
    ALLOWED_HOSTS = ['localhost']

try:
    from django.contrib.sites.models import Site
    site_host = Site.objects.get(id=SITE_ID).domain
    if site_host and site_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(site_host)
except Exception:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Configurazione Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise Exception('DJANGO_SECRET_KEY deve essere impostata in produzione!')

# Override static/media per produzione
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# Override email backend per produzione
EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('DJANGO_EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'webmaster@localhost'

CUPS_HOST = os.getenv("CUPS_HOST", "localhost")
CUPS_PORT = os.getenv("CUPS_PORT", "631")