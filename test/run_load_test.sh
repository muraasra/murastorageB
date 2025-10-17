#!/bin/bash
# Script de test de charge pour le backend Django

echo "🚀 Test de charge - Backend Django"
echo "=================================="

# Vérifier que le serveur Django est démarré
if ! curl -s http://127.0.0.1:8000/api/ > /dev/null; then
    echo "❌ Le serveur Django n'est pas démarré sur http://127.0.0.1:8000"
    echo "   Démarrez le serveur avec: python manage.py runserver"
    exit 1
fi

echo "✅ Serveur Django détecté"

# Installer les dépendances si nécessaire
if ! python -c "import aiohttp" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip install aiohttp
fi

# Lancer le test de charge
echo "🏃 Lancement du test de charge..."
python test/load_test.py

echo "✅ Test terminé"
