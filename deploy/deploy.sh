#!/bin/bash
# Script de déploiement simple pour PythonAnywhere

echo "🚀 Déploiement sur PythonAnywhere..."

# Variables (à modifier selon votre configuration)
PROJECT_DIR="/home/yourusername/walner-durel/Backend"
VENV_DIR="/home/yourusername/.virtualenvs/walner-durel"

# Se déplacer dans le répertoire du projet
cd "$PROJECT_DIR"

# Mettre à jour le code
echo "📥 Mise à jour du code..."
git pull origin main

# Activer l'environnement virtuel
echo "🐍 Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# Redémarrer l'application
echo "🔄 Redémarrage de l'application..."
touch storage/wsgi.py

echo "✅ Déploiement terminé !"
echo "🌐 Application: https://yourusername.pythonanywhere.com"