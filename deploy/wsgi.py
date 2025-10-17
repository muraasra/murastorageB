# Configuration WSGI simple pour PythonAnywhere

import os
import sys

# Ajouter le chemin du projet
path = '/home/yourusername/walner-durel/Backend'
if path not in sys.path:
    sys.path.append(path)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings_production')

# Application Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()