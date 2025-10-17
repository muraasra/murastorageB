#!/bin/bash

echo "🚀 Configuration Redis pour les optimisations de performance"

# Vérifier si Redis est installé
if ! command -v redis-server &> /dev/null; then
    echo "📦 Installation de Redis..."
    
    # Détection du système d'exploitation
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install redis-server -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install redis
        else
            echo "❌ Homebrew non trouvé. Installez Redis manuellement."
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows (Git Bash)
        echo "⚠️  Windows détecté. Installez Redis manuellement:"
        echo "   1. Téléchargez Redis depuis: https://github.com/microsoftarchive/redis/releases"
        echo "   2. Ou utilisez WSL: wsl --install"
        echo "   3. Ou utilisez Docker: docker run -d -p 6379:6379 redis:alpine"
        exit 1
    else
        echo "❌ Système d'exploitation non supporté: $OSTYPE"
        exit 1
    fi
else
    echo "✅ Redis déjà installé"
fi

# Démarrer Redis
echo "🔄 Démarrage de Redis..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start redis
fi

# Vérifier que Redis fonctionne
echo "🔍 Vérification de Redis..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis fonctionne correctement"
else
    echo "❌ Redis ne répond pas. Vérifiez l'installation."
    exit 1
fi

# Configuration Redis pour la production
echo "⚙️  Configuration Redis pour la production..."

# Créer le fichier de configuration Redis
cat > redis-production.conf << EOF
# Configuration Redis pour la production
port 6379
bind 127.0.0.1
timeout 300
tcp-keepalive 60

# Persistance
save 900 1
save 300 10
save 60 10000

# Mémoire
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logs
loglevel notice
logfile /var/log/redis/redis-server.log

# Sécurité
requirepass your_redis_password_here
EOF

echo "📝 Fichier de configuration créé: redis-production.conf"
echo "🔐 N'oubliez pas de changer le mot de passe Redis!"

# Test de performance Redis
echo "🧪 Test de performance Redis..."
python3 << 'EOF'
import redis
import time

# Connexion Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Test de performance
start_time = time.time()
for i in range(1000):
    r.set(f"test_key_{i}", f"test_value_{i}")
    r.get(f"test_key_{i}")
end_time = time.time()

duration = end_time - start_time
ops_per_second = 2000 / duration  # 2000 opérations (1000 set + 1000 get)

print(f"✅ Performance Redis: {ops_per_second:.0f} opérations/seconde")
print(f"⏱️  Durée: {duration:.3f}s")

# Nettoyage
for i in range(1000):
    r.delete(f"test_key_{i}")

print("🧹 Test terminé et nettoyé")
EOF

echo ""
echo "🎉 Configuration Redis terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Modifiez le mot de passe dans redis-production.conf"
echo "   2. Redémarrez Redis avec la nouvelle configuration"
echo "   3. Testez les performances avec: python manage.py performance_test"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Démarrer Redis: redis-server"
echo "   - Arrêter Redis: redis-cli shutdown"
echo "   - Monitorer Redis: redis-cli monitor"
echo "   - Statistiques: redis-cli info stats"




