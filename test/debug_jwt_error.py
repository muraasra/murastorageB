#!/usr/bin/env python3
"""
Script de debug pour identifier l'erreur JWT
"""

import os
import django
import sys

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.serializers import CustomTokenObtainPairSerializer

User = get_user_model()

def debug_jwt_serializer():
    """Debug du serializer JWT"""
    print("🔍 DEBUG - Serializer JWT")
    print("=" * 50)
    
    try:
        # Récupérer un utilisateur existant
        user = User.objects.filter(entreprise__isnull=False).first()
        if not user:
            print("❌ Aucun utilisateur avec entreprise trouvé")
            return
        
        print(f"👤 Utilisateur test: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Rôle: {user.role}")
        print(f"   Entreprise: {user.entreprise.nom if user.entreprise else 'Aucune'}")
        print(f"   Boutique: {user.boutique.nom if user.boutique else 'Aucune'}")
        
        # Test du serializer
        print(f"\n🧪 Test du serializer JWT...")
        
        # Créer des données de test
        test_data = {
            'username': user.username,
            'password': 'testpassword123'  # Mot de passe de test
        }
        
        serializer = CustomTokenObtainPairSerializer(data=test_data)
        
        if serializer.is_valid():
            print("✅ Serializer valide")
            response_data = serializer.validate(test_data)
            print(f"📊 Données de réponse: {len(response_data)} champs")
            
            # Afficher les clés principales
            print(f"   Access token: {'access' in response_data}")
            print(f"   Refresh token: {'refresh' in response_data}")
            print(f"   User data: {'user' in response_data}")
            print(f"   Entreprise data: {'entreprise' in response_data}")
            print(f"   Boutique data: {'boutique' in response_data}")
            print(f"   Statistics: {'statistics' in response_data}")
            print(f"   Permissions: {'permissions' in response_data}")
            
        else:
            print("❌ Serializer invalide")
            print(f"   Erreurs: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_token_creation():
    """Test de création de token"""
    print(f"\n🔑 Test de création de token...")
    
    try:
        user = User.objects.filter(entreprise__isnull=False).first()
        if not user:
            print("❌ Aucun utilisateur avec entreprise trouvé")
            return
        
        # Test de création de token JWT
        token = CustomTokenObtainPairSerializer.get_token(user)
        print(f"✅ Token créé avec succès")
        print(f"   Token type: {type(token)}")
        
        # Vérifier les claims du token
        print(f"📋 Claims du token:")
        for key, value in token.items():
            if isinstance(value, str) and len(value) > 50:
                print(f"   {key}: {value[:30]}...")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Erreur création token: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_jwt_serializer()
    test_token_creation()
