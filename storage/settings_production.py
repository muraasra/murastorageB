# Configuration Django pour la production sur PythonAnywhere

import os
from .settings import *

# Configuration de base
DEBUG = False
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'www.yourusername.pythonanywhere.com',
]

# Base de données MySQL (PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'yourusername$walner_durel'),
        'USER': os.environ.get('DB_USER', 'yourusername'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/walner-durel/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/yourusername/walner-durel/media/'

# Cache simple
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
    }
}