INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# django-allauth e dipendenze
INSTALLED_APPS += [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    'django_htmx',
    'template_partials',
    'widget_tweaks',
    'import_export',
    'django_filters',
    'accounts',
    'printers',
    'sagragest',
    'sagrarapid',
    'reports',
]
