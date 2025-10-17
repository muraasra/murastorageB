#!/usr/bin/env python3
"""
Test de vérification de l'authentification JWT
- Tester l'authentification JWT avec différents utilisateurs
- Vérifier que les tokens sont valides
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_jwt_with_different_users():
    """Test JWT avec différents utilisateurs."""
    print("🔐 TEST AUTHENTIFICATION JWT")
    print("=" * 35)
    
    # Liste des utilisateurs à tester
    users_to_test = [
        {"username": "testuser", "email": "testuser@test.com", "password": "admin123"},
        {"username": "test", "email": "admin@test.com", "password": "admin123"},
        {"username": "filtertest", "email": "filtertest@test.com", "password": "admin123"},
    ]
    
    successful_logins = []
    
    for user in users_to_test:
        print(f"\n👤 Test avec: {user['username']} ({user['email']})")
        
        # Test avec username
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
            print(f"   📥 Statut (username): {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Connexion réussie avec username!")
                print(f"   🔑 Token: {data.get('access', '')[:20]}...")
                print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
                print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
                successful_logins.append({
                    "method": "username",
                    "user": user["username"],
                    "token": data.get('access'),
                    "user_id": data.get('user', {}).get('id'),
                    "entreprise_id": data.get('entreprise', {}).get('id')
                })
            else:
                print(f"   ❌ Erreur (username): {response.json()}")
        except Exception as e:
            print(f"   ❌ Exception (username): {e}")
        
        # Test avec email
        login_data = {
            "username": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
            print(f"   📥 Statut (email): {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Connexion réussie avec email!")
                print(f"   🔑 Token: {data.get('access', '')[:20]}...")
                print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
                print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
                successful_logins.append({
                    "method": "email",
                    "user": user["username"],
                    "token": data.get('access'),
                    "user_id": data.get('user', {}).get('id'),
                    "entreprise_id": data.get('entreprise', {}).get('id')
                })
            else:
                print(f"   ❌ Erreur (email): {response.json()}")
        except Exception as e:
            print(f"   ❌ Exception (email): {e}")
    
    return successful_logins

def test_jwt_token_validation(token):
    """Test de validation du token JWT."""
    print(f"\n🔍 TEST VALIDATION TOKEN JWT")
    print("=" * 35)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec un endpoint protégé
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"📥 Statut endpoint protégé: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token JWT valide!")
            print(f"   👥 Utilisateurs récupérés: {len(data)}")
            return True
        else:
            print(f"❌ Token JWT invalide: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Exception validation: {e}")
        return False

def test_jwt_refresh_token(refresh_token):
    """Test du refresh token JWT."""
    print(f"\n🔄 TEST REFRESH TOKEN JWT")
    print("=" * 30)
    
    refresh_data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/refresh/", json=refresh_data)
        print(f"📥 Statut refresh: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Refresh token réussi!")
            print(f"   🔑 Nouveau token: {data.get('access', '')[:20]}...")
            return data.get('access')
        else:
            print(f"❌ Erreur refresh: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Exception refresh: {e}")
        return None

def main():
    print("🚀 VÉRIFICATION AUTHENTIFICATION JWT")
    print("=" * 45)
    
    # 1. Test avec différents utilisateurs
    successful_logins = test_jwt_with_different_users()
    
    if not successful_logins:
        print(f"\n❌ AUCUNE CONNEXION JWT RÉUSSIE")
        print(f"   - Vérifier les utilisateurs existants")
        print(f"   - Vérifier les mots de passe")
        print(f"   - Vérifier la configuration JWT")
        return
    
    print(f"\n✅ {len(successful_logins)} connexion(s) JWT réussie(s)")
    
    # 2. Test de validation du token
    first_login = successful_logins[0]
    token_valid = test_jwt_token_validation(first_login["token"])
    
    # 3. Résumé
    print(f"\n📊 RÉSUMÉ JWT")
    print("=" * 20)
    print(f"   🔐 Connexions réussies: {len(successful_logins)}")
    print(f"   🔍 Token validation: {'✅' if token_valid else '❌'}")
    
    if successful_logins and token_valid:
        print(f"\n🎉 AUTHENTIFICATION JWT FONCTIONNE!")
        print(f"   ✅ Les connexions JWT réussissent")
        print(f"   ✅ Les tokens sont valides")
        print(f"   ✅ Les endpoints protégés sont accessibles")
        
        # Afficher les méthodes qui fonctionnent
        methods = set(login["method"] for login in successful_logins)
        print(f"   📋 Méthodes fonctionnelles: {', '.join(methods)}")
    else:
        print(f"\n⚠️  PROBLÈMES JWT DÉTECTÉS")
        print(f"   - Vérifier la configuration JWT")
        print(f"   - Vérifier les utilisateurs de test")

if __name__ == "__main__":
    main()

























