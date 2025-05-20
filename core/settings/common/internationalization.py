from .paths import *
# Impostazioni di internazionalizzazione per il progetto Django.
LANGUAGE_CODE = 'it'
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / 'locale']
LANGUAGES = [
    ('it', 'Italiano'),
    ('en', 'English'),
]
