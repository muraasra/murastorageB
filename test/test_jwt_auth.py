#!/usr/bin/env python3
"""
Script de test pour l'authentification JWT avec informations complètes
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

def test_jwt_authentication():
    """Test de l'authentification JWT avec informations complètes"""
    print("🔐 TEST AUTHENTIFICATION JWT - Informations Complètes")
    print("=" * 70)
    
    # Utiliser un utilisateur existant avec entreprise
    email = "test.auth.1759282506@example.com"
    password = "testpassword123"
    
    # 1. Test de connexion JWT
    print("1️⃣ Connexion JWT...")
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion JWT réussie!")
            print(f"📊 Statut: {response.status_code}")
            
            # Afficher toutes les informations reçues
            print(f"\n📄 RÉPONSE COMPLÈTE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extraire les tokens
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            
            if access_token:
                print(f"\n🔑 Tokens:")
                print(f"   Access Token: {access_token[:50]}...")
                print(f"   Refresh Token: {refresh_token[:50]}...")
            
            # Informations utilisateur
            user_data = data.get('user', {})
            if user_data:
                print(f"\n👤 Informations utilisateur:")
                print(f"   ID: {user_data.get('id')}")
                print(f"   Nom: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Rôle: {user_data.get('role')}")
                print(f"   Téléphone: {user_data.get('telephone')}")
                print(f"   Poste: {user_data.get('poste')}")
                print(f"   Employé actif: {user_data.get('is_active_employee')}")
            
            # Informations entreprise
            entreprise_data = data.get('entreprise', {})
            if entreprise_data:
                print(f"\n🏢 Informations entreprise:")
                print(f"   ID: {entreprise_data.get('id_entreprise')}")
                print(f"   Nom: {entreprise_data.get('nom')}")
                print(f"   Secteur: {entreprise_data.get('secteur_activite')}")
                print(f"   Ville: {entreprise_data.get('ville')}")
                print(f"   Pack: {entreprise_data.get('pack_type')}")
                print(f"   Employés: {entreprise_data.get('nombre_employes')}")
                print(f"   Année création: {entreprise_data.get('annee_creation')}")
            
            # Informations boutique
            boutique_data = data.get('boutique', {})
            if boutique_data:
                print(f"\n🏪 Informations boutique:")
                print(f"   ID: {boutique_data.get('id')}")
                print(f"   Nom: {boutique_data.get('nom')}")
                print(f"   Ville: {boutique_data.get('ville')}")
                print(f"   Responsable: {boutique_data.get('responsable')}")
            
            # Statistiques
            stats = data.get('statistics', {})
            if stats:
                print(f"\n📊 Statistiques:")
                print(f"   Produits: {stats.get('total_produits')}")
                print(f"   Factures: {stats.get('total_factures')}")
                print(f"   Boutiques: {stats.get('total_boutiques')}")
                print(f"   Utilisateurs: {stats.get('total_utilisateurs')}")
            
            # Permissions
            permissions = data.get('permissions', {})
            if permissions:
                print(f"\n🔐 Permissions:")
                for perm, value in permissions.items():
                    status = "✅" if value else "❌"
                    print(f"   {status} {perm.replace('_', ' ').title()}")
            
            # 2. Test d'utilisation du token
            print(f"\n2️⃣ Test d'utilisation du token...")
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
            
            # 3. Test de refresh token
            print(f"\n3️⃣ Test de refresh token...")
            refresh_data = {"refresh": refresh_token}
            
            try:
                response = requests.post(f"{BASE_URL}/auth/jwt/refresh/", json=refresh_data, headers=HEADERS)
                if response.status_code == 200:
                    refresh_response = response.json()
                    new_access_token = refresh_response.get('access')
                    print("✅ Refresh token fonctionne")
                    print(f"   Nouveau access token: {new_access_token[:50]}...")
                else:
                    print(f"❌ Refresh token échoué - Statut: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur refresh token: {e}")
            
            # 4. Test de vérification token
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

def test_jwt_vs_token():
    """Comparaison JWT vs Token authentication"""
    print(f"\n🔄 COMPARAISON JWT vs TOKEN")
    print("=" * 50)
    
    email = "test.auth.1759282506@example.com"
    password = "testpassword123"
    login_data = {"username": email, "password": password}
    
    # Test JWT
    print("🔐 Test JWT:")
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            jwt_data = response.json()
            print(f"   ✅ JWT - Access token: {jwt_data.get('access', '')[:30]}...")
            print(f"   📊 JWT - Informations: {len(jwt_data)} champs")
        else:
            print(f"   ❌ JWT échoué: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur JWT: {e}")
    
    # Test Token
    print("🔑 Test Token:")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Token - Token: {token_data.get('token', '')[:30]}...")
            print(f"   📊 Token - Informations: {len(token_data)} champs")
        else:
            print(f"   ❌ Token échoué: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur Token: {e}")

if __name__ == "__main__":
    test_jwt_authentication()
    test_jwt_vs_token()
