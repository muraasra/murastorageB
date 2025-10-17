#!/usr/bin/env python3
"""
Test complet de l'authentification JWT avec toutes les informations
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

def test_jwt_complete():
    """Test complet de JWT avec affichage de toutes les informations"""
    print("🔐 TEST COMPLET JWT - Informations Complètes")
    print("=" * 70)
    
    # Données de connexion
    login_data = {
        "username": "test.auth.1759282506@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Connexion JWT
        print("1️⃣ Connexion JWT...")
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion JWT réussie!")
            
            # Afficher toutes les informations
            print(f"\n📄 RÉPONSE COMPLÈTE JWT:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extraire les tokens
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            
            print(f"\n🔑 TOKENS:")
            print(f"   Access Token: {access_token[:80]}...")
            print(f"   Refresh Token: {refresh_token[:80]}...")
            
            # Informations utilisateur
            user_data = data.get('user', {})
            print(f"\n👤 INFORMATIONS UTILISATEUR:")
            for key, value in user_data.items():
                print(f"   {key}: {value}")
            
            # Informations entreprise
            entreprise_data = data.get('entreprise', {})
            if entreprise_data:
                print(f"\n🏢 INFORMATIONS ENTREPRISE:")
                for key, value in entreprise_data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"\n🏢 INFORMATIONS ENTREPRISE: Aucune")
            
            # Informations boutique
            boutique_data = data.get('boutique', {})
            if boutique_data:
                print(f"\n🏪 INFORMATIONS BOUTIQUE:")
                for key, value in boutique_data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"\n🏪 INFORMATIONS BOUTIQUE: Aucune")
            
            # Permissions
            permissions = data.get('permissions', {})
            print(f"\n🔐 PERMISSIONS:")
            for perm, value in permissions.items():
                status = "✅" if value else "❌"
                print(f"   {status} {perm.replace('_', ' ').title()}")
            
            # Test d'utilisation du token
            print(f"\n2️⃣ Test d'utilisation du token JWT...")
            auth_headers = HEADERS.copy()
            auth_headers['Authorization'] = f'Bearer {access_token}'
            
            try:
                response = requests.get(f"{BASE_URL}/entreprises/", headers=auth_headers)
                if response.status_code == 200:
                    print("✅ Token JWT fonctionne - Accès aux APIs autorisé")
                else:
                    print(f"❌ Token JWT ne fonctionne pas - Statut: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur test token: {e}")
            
            # Test de refresh token
            print(f"\n3️⃣ Test de refresh token...")
            refresh_data = {"refresh": refresh_token}
            
            try:
                response = requests.post(f"{BASE_URL}/auth/jwt/refresh/", json=refresh_data, headers=HEADERS)
                if response.status_code == 200:
                    refresh_response = response.json()
                    new_access_token = refresh_response.get('access')
                    print("✅ Refresh token fonctionne")
                    print(f"   Nouveau access token: {new_access_token[:80]}...")
                else:
                    print(f"❌ Refresh token échoué - Statut: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur refresh token: {e}")
            
            # Test de vérification token
            print(f"\n4️⃣ Test de vérification token...")
            verify_data = {"token": access_token}
            
            try:
                response = requests.post(f"{BASE_URL}/auth/jwt/verify/", json=verify_data, headers=HEADERS)
                if response.status_code == 200:
                    print("✅ Vérification token réussie")
                else:
                    print(f"❌ Vérification token échouée - Statut: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur vérification token: {e}")
                
        else:
            print(f"❌ Échec connexion JWT - Statut: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")

def compare_auth_methods():
    """Comparaison entre JWT et Token authentication"""
    print(f"\n🔄 COMPARAISON JWT vs TOKEN")
    print("=" * 50)
    
    login_data = {
        "username": "test.auth.1759282506@example.com",
        "password": "testpassword123"
    }
    
    # Test JWT
    print("🔐 Test JWT:")
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            jwt_data = response.json()
            print(f"   ✅ JWT - Access token: {jwt_data.get('access', '')[:50]}...")
            print(f"   📊 JWT - Informations: {len(jwt_data)} champs")
            print(f"   🔑 JWT - Refresh token: {'refresh' in jwt_data}")
            print(f"   👤 JWT - User data: {'user' in jwt_data}")
            print(f"   🏢 JWT - Entreprise data: {'entreprise' in jwt_data}")
            print(f"   🏪 JWT - Boutique data: {'boutique' in jwt_data}")
            print(f"   🔐 JWT - Permissions: {'permissions' in jwt_data}")
        else:
            print(f"   ❌ JWT échoué: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur JWT: {e}")
    
    # Test Token
    print("\n🔑 Test Token:")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Token - Token: {token_data.get('token', '')[:50]}...")
            print(f"   📊 Token - Informations: {len(token_data)} champs")
            print(f"   🔑 Token - Refresh token: {'refresh' in token_data}")
            print(f"   👤 Token - User data: {'user' in token_data}")
            print(f"   🏢 Token - Entreprise data: {'entreprise' in token_data}")
            print(f"   🏪 Token - Boutique data: {'boutique' in token_data}")
            print(f"   🔐 Token - Permissions: {'permissions' in token_data}")
        else:
            print(f"   ❌ Token échoué: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Token: {e}")

if __name__ == "__main__":
    test_jwt_complete()
    compare_auth_methods()
