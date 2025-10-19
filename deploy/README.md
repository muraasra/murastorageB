# 🚀 Déploiement Simple PythonAnywhere

## 📋 Étapes de Configuration

### 1. Créer un compte PythonAnywhere
- Allez sur [pythonanywhere.com](https://www.pythonanywhere.com)
- Créez un compte gratuit

### 2. Configurer l'environnement
```bash
# Créer l'environnement virtuel
mkvirtualenv --python=/usr/bin/python3.12 walner-durel

# Cloner le projet
git clone https://github.com/yourusername/walner-durel.git
cd walner-durel/Backend
```

### 3. Configurer les variables
```bash
# Copier le fichier d'exemple
cp deploy/env_example.txt .env

# Modifier les valeurs dans .env
# - Remplacez 'yourusername' par votre nom d'utilisateur
# - Configurez le mot de passe de la base de données
```

### 4. Créer la base de données
- Dans PythonAnywhere, allez dans l'onglet "Databases"
- Créez une base de données MySQL
- Notez le nom et le mot de passe

### 5. Configurer WSGI
- Dans PythonAnywhere, allez dans l'onglet "Web"
- Configurez le fichier WSGI avec le contenu de `deploy/wsgi.py`
- Modifiez le chemin selon votre nom d'utilisateur

### 6. Déployer
```bash
# Rendre le script exécutable
chmod +x deploy/deploy.sh

# Exécuter le déploiement
./deploy/deploy.sh
```

## 📁 Fichiers Essentiels

- `deploy/deploy.sh` - Script de déploiement
- `deploy/wsgi.py` - Configuration WSGI
- `deploy/env_example.txt` - Variables d'environnement
- `storage/settings_production.py` - Configuration de production
- `requirements.txt` - Dépendances Python

## 🔧 Configuration WSGI

```python
import os
import sys

path = '/home/yourusername/walner-durel/Backend'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## ✅ Checklist

- [ ] Compte PythonAnywhere créé
- [ ] Environnement virtuel configuré
- [ ] Projet cloné
- [ ] Variables d'environnement configurées
- [ ] Base de données créée
- [ ] WSGI configuré
- [ ] Premier déploiement réussi

**🎉 Votre application est déployée !**






