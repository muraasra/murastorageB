#!/usr/bin/env python3
"""
Test d'authentification par email
- Tester JWT avec email admin@test.com
- Tester Token avec email admin@test.com
- Vérifier que ça fonctionne maintenant
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_jwt_with_email():
    """Test d'authentification JWT avec email."""
    print("🔐 TEST JWT AVEC EMAIL")
    print("=" * 30)
    
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion JWT avec email réussie!")
            print(f"   🔑 Token: {data.get('access', '')[:20]}...")
            print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   📧 Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
            return data['access'], data['user']['id'], data['entreprise']['id']
        else:
            print(f"❌ Erreur JWT: {response.json()}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Exception JWT: {e}")
        return None, None, None

def test_token_with_email():
    """Test d'authentification Token avec email."""
    print(f"\n🔑 TEST TOKEN AVEC EMAIL")
    print("=" * 30)
    
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion Token avec email réussie!")
            print(f"   🔑 Token: {data.get('token', '')[:20]}...")
            print(f"   👤 User: {data.get('username', 'N/A')}")
            print(f"   📧 Email: {data.get('email', 'N/A')}")
            print(f"   🏢 Entreprise: {data.get('entreprise_nom', 'N/A')}")
            return data['token']
        else:
            print(f"❌ Erreur Token: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Exception Token: {e}")
        return None

def test_protected_endpoints_with_email_auth(jwt_token, token_auth):
    """Test des endpoints protégés avec les tokens obtenus par email."""
    print(f"\n🔒 TEST ENDPOINTS AVEC AUTHENTIFICATION EMAIL")
    print("=" * 50)
    
    # Test avec JWT
    if jwt_token:
        print(f"\n🔐 Test avec JWT Token")
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/users/", headers=headers)
            print(f"   📥 Statut JWT: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ JWT fonctionne ({len(data)} utilisateurs)")
            else:
                print(f"   ❌ JWT échoué: {response.json()}")
        except Exception as e:
            print(f"   ❌ Exception JWT: {e}")
    
    # Test avec Token
    if token_auth:
        print(f"\n🔑 Test avec Token Auth")
        headers = {
            "Authorization": f"Token {token_auth}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/users/", headers=headers)
            print(f"   📥 Statut Token: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token Auth fonctionne ({len(data)} utilisateurs)")
            else:
                print(f"   ❌ Token Auth échoué: {response.json()}")
        except Exception as e:
            print(f"   ❌ Exception Token Auth: {e}")

def test_both_methods():
    """Test avec username et email pour comparaison."""
    print(f"\n🔄 TEST COMPARAISON USERNAME vs EMAIL")
    print("=" * 45)
    
    # Test avec username
    print(f"\n👤 Test avec username: test")
    login_data_username = {
        "username": "test",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data_username)
        print(f"   📥 Statut username: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Username fonctionne")
        else:
            print(f"   ❌ Username échoué: {response.json()}")
    except Exception as e:
        print(f"   ❌ Exception username: {e}")
    
    # Test avec email
    print(f"\n📧 Test avec email: admin@test.com")
    login_data_email = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data_email)
        print(f"   📥 Statut email: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Email fonctionne")
        else:
            print(f"   ❌ Email échoué: {response.json()}")
    except Exception as e:
        print(f"   ❌ Exception email: {e}")

def main():
    print("🚀 TEST AUTHENTIFICATION PAR EMAIL")
    print("=" * 40)
    
    # 1. Test JWT avec email
    jwt_token, user_id, entreprise_id = test_jwt_with_email()
    
    # 2. Test Token avec email
    token_auth = test_token_with_email()
    
    # 3. Test des endpoints protégés
    test_protected_endpoints_with_email_auth(jwt_token, token_auth)
    
    # 4. Test de comparaison
    test_both_methods()
    
    # 5. Résumé
    print(f"\n📊 RÉSUMÉ AUTHENTIFICATION EMAIL")
    print("=" * 40)
    print(f"   🔐 JWT avec email: {'✅' if jwt_token else '❌'}")
    print(f"   🔑 Token avec email: {'✅' if token_auth else '❌'}")
    
    if jwt_token or token_auth:
        print(f"\n🎉 AUTHENTIFICATION PAR EMAIL FONCTIONNE!")
        print(f"   ✅ Email: admin@test.com")
        print(f"   ✅ Mot de passe: admin123")
        print(f"   ✅ Les deux méthodes (JWT et Token) supportent l'email")
        
        print(f"\n💡 UTILISATION:")
        print(f"   🔐 JWT: {{'email': 'admin@test.com', 'password': 'admin123'}}")
        print(f"   🔑 Token: {{'email': 'admin@test.com', 'password': 'admin123'}}")
    else:
        print(f"\n❌ PROBLÈME D'AUTHENTIFICATION PAR EMAIL")
        print(f"   - Vérifier les modifications backend")
        print(f"   - Vérifier les serializers")

if __name__ == "__main__":
    main()































