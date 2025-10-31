#!/bin/bash
# Script de configuration des notifications pour PythonAnywhere
# À exécuter une fois après le déploiement

echo "=========================================="
echo "Configuration des Notifications Automatiques"
echo "=========================================="
echo ""

# Chemin du projet (à adapter selon votre chemin PythonAnywhere)
PROJECT_PATH="/home/murastorage/walner-durel/Backend"

# Test de la commande
echo "Test de la commande de notifications..."
cd "$PROJECT_PATH"
python3.10 manage.py send_notifications --help

if [ $? -eq 0 ]; then
    echo "✅ Commande testée avec succès!"
else
    echo "❌ Erreur lors du test de la commande"
    exit 1
fi

echo ""
echo "=========================================="
echo "Instructions pour PythonAnywhere:"
echo "=========================================="
echo ""
echo "1. Connectez-vous à PythonAnywhere"
echo "2. Allez dans l'onglet 'Tasks'"
echo "3. Créez une nouvelle tâche avec:"
echo ""
echo "   Command: python3.10 $PROJECT_PATH/manage.py send_notifications"
echo "   Hour: 8"
echo "   Minute: 0"
echo ""
echo "4. Optionnel: Créez une tâche pour les alertes urgentes (toutes les 2h):"
echo ""
echo "   Command: python3.10 $PROJECT_PATH/manage.py send_notifications --stock"
echo "   Hour: */2"
echo "   Minute: 0"
echo ""
echo "=========================================="

