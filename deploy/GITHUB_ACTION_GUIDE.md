# 🚀 GitHub Action - Déploiement PythonAnywhere

## 📋 Configuration GitHub Action

### 1. Créer le fichier GitHub Action
Le fichier `.github/workflows/deploy.yml` est déjà créé dans votre projet.

### 2. Configurer les Secrets GitHub

#### **Étape 1 : Aller dans GitHub**
1. Allez sur votre repository GitHub
2. Cliquez sur **Settings** (en haut à droite)
3. Dans le menu de gauche, cliquez sur **Secrets and variables** → **Actions**

#### **Étape 2 : Ajouter les secrets**
Cliquez sur **New repository secret** et ajoutez ces 3 secrets :

**Secret 1 : `PYTHONANYWHERE_HOST`**
- **Nom** : `PYTHONANYWHERE_HOST`
- **Valeur** : `ssh.pythonanywhere.com`

**Secret 2 : `PYTHONANYWHERE_USERNAME`**
- **Nom** : `PYTHONANYWHERE_USERNAME`
- **Valeur** : `votre_nom_utilisateur_pythonanywhere`

**Secret 3 : `PYTHONANYWHERE_SSH_KEY`**
- **Nom** : `PYTHONANYWHERE_SSH_KEY`
- **Valeur** : `votre_clé_ssh_privée`

### 3. Générer une clé SSH

#### **Sur votre machine locale :**
```bash
# Générer une nouvelle clé SSH
ssh-keygen -t rsa -b 4096 -C "votre_email@example.com"

# Copier la clé publique
cat ~/.ssh/id_rsa.pub
```

#### **Sur PythonAnywhere :**
1. Allez dans l'onglet **Account** sur PythonAnywhere
2. Cliquez sur **SSH key**
3. Collez votre clé publique dans le champ
4. Sauvegardez

#### **Copier la clé privée :**
```bash
# Copier la clé privée (pour le secret GitHub)
cat ~/.ssh/id_rsa
```

### 4. Configuration PythonAnywhere

#### **Étape 1 : Cloner le projet**
```bash
# Dans le terminal PythonAnywhere
git clone https://github.com/votre_username/walner-durel.git
cd walner-durel/Backend
```

#### **Étape 2 : Configurer l'environnement virtuel**
```bash
# Créer l'environnement virtuel
mkvirtualenv --python=/usr/bin/python3.12 walner-durel

# Activer l'environnement
workon walner-durel

# Installer les dépendances
pip install -r requirements.txt
```

#### **Étape 3 : Configurer la base de données**
1. Allez dans l'onglet **Databases** sur PythonAnywhere
2. Créez une base de données MySQL
3. Notez le nom et le mot de passe

#### **Étape 4 : Configurer WSGI**
1. Allez dans l'onglet **Web** sur PythonAnywhere
2. Configurez le fichier WSGI avec ce contenu :

```python
import os
import sys

path = '/home/votre_username/walner-durel/Backend'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. Test du déploiement

#### **Méthode 1 : Push automatique**
1. Faites un commit et push sur la branche `main`
2. Le déploiement se déclenche automatiquement
3. Vérifiez dans l'onglet **Actions** de GitHub

#### **Méthode 2 : Déclenchement manuel**
1. Allez dans l'onglet **Actions** de GitHub
2. Cliquez sur **Deploy to PythonAnywhere**
3. Cliquez sur **Run workflow**

### 6. Vérification

#### **Vérifier le déploiement :**
1. Allez sur votre URL PythonAnywhere : `https://votre_username.pythonanywhere.com`
2. Vérifiez que l'application fonctionne
3. Consultez les logs dans l'onglet **Tasks** de PythonAnywhere

## 🔧 Dépannage

### **Erreur de connexion SSH :**
- Vérifiez que la clé SSH est correctement configurée
- Vérifiez que le nom d'utilisateur est correct

### **Erreur de permissions :**
- Vérifiez que le répertoire existe sur PythonAnywhere
- Vérifiez que l'environnement virtuel est configuré

### **Erreur de base de données :**
- Vérifiez que la base de données est créée
- Vérifiez les paramètres de connexion

## ✅ Checklist

- [ ] Repository GitHub créé
- [ ] Fichier `.github/workflows/deploy.yml` présent
- [ ] 3 secrets GitHub configurés
- [ ] Clé SSH générée et configurée
- [ ] Projet cloné sur PythonAnywhere
- [ ] Environnement virtuel configuré
- [ ] Base de données créée
- [ ] WSGI configuré
- [ ] Premier déploiement réussi

**🎉 Votre déploiement automatique est configuré !**

Maintenant, à chaque push sur `main`, votre application se déploie automatiquement sur PythonAnywhere.






