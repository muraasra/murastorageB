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

# Cache simple (LocMemCache) avec TTL très court (30s max)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 30,  # 30 secondes
    }
}

# Configuration CORS pour le frontend
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://murastorage.netlify.app",
    "https://murastorage.pythonanywhere.com",
]

# Email production — Hostinger SMTP
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '465'))
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'MuraStorage <support@murastorage.com>'
SERVER_EMAIL = 'support@murastorage.com'

if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    raise ValueError("Email configuration incomplete - EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD must be set in environment variables")

CORS_ALLOWED_ORIGINS = [
    "https://murastorage.pythonanywhere.com",
    "https://www.murastorage.pythonanywhere.com",
    "https://murastorage.netlify.app",  # Frontend Netlify
    "http://localhost:3000",  # Pour le développement local
]