# Configuration Django pour la production sur PythonAnywhere

import os
from .settings import *

# Configuration de base
DEBUG = False
ALLOWED_HOSTS = [
    'murastorage.pythonanywhere.com',
    'www.murastorage.pythonanywhere.com',
]

# Base de données MySQL (PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'murastorage$walner_durel'),
        'USER': os.environ.get('DB_USER', 'murastorage'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('DB_HOST', 'murastorage.mysql.pythonanywhere-services.com'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = '/home/murastorage/walner-durel/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/murastorage/walner-durel/media/'

# Cache simple
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
    }
}

# Configuration CORS pour le frontend
CORS_ALLOWED_ORIGINS = [
    "https://murastorage.pythonanywhere.com",
    "https://www.murastorage.pythonanywhere.com",
    "https://murastorage.netlify.app",  # Frontend Netlify
    "http://localhost:3000",  # Pour le développement local
]