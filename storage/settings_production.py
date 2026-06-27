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

# Email production
# PythonAnywhere bloque smtp.hostinger.com (port 465) — utiliser Gmail ou un relai whitelist
# Pour Gmail: EMAIL_HOST=smtp.gmail.com, EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False
# + créer un App Password Google (Compte > Sécurité > Mots de passe des applications)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
_port_str = os.environ.get('EMAIL_PORT', '587')
EMAIL_PORT = int(_port_str) if _port_str else 587
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', f'MuraStorage <{EMAIL_HOST_USER}>')
SERVER_EMAIL = EMAIL_HOST_USER

if not all([EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    import logging
    logging.getLogger('django').warning(
        "Email non configuré (EMAIL_HOST_USER ou EMAIL_HOST_PASSWORD manquant) — "
        "les emails de vérification ne seront pas envoyés."
    )

CORS_ALLOWED_ORIGINS = [
    "https://murastorage.pythonanywhere.com",
    "https://www.murastorage.pythonanywhere.com",
    "https://murastorage.netlify.app",  # Frontend Netlify
    "http://localhost:3000",  # Pour le développement local
]