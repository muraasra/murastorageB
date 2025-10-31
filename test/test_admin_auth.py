#!/usr/bin/env python3
"""
Test d'authentification pour admin@test.com
- Tester avec username et email
- Vérifier l'authentification JWT et Token
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_admin_jwt_auth():
    """Test d'authentification JWT pour admin@test.com."""
    print("🔐 TEST AUTHENTIFICATION JWT ADMIN")
    print("=" * 40)
    
    # Test avec username
    print(f"\n👤 Test avec username: test")
    login_data = {
        "username": "test",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion JWT réussie!")
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

def test_admin_token_auth():
    """Test d'authentification Token pour admin@test.com."""
    print(f"\n🔑 TEST AUTHENTIFICATION TOKEN ADMIN")
    print("=" * 40)
    
    # Test avec username
    print(f"\n👤 Test avec username: test")
    login_data = {
        "username": "test",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion Token réussie!")
            print(f"   🔑 Token: {data.get('token', '')[:20]}...")
            print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   📧 Email: {data.get('user', {}).get('email', 'N/A')}")
            return data['token']
        else:
            print(f"❌ Erreur Token: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Exception Token: {e}")
        return None

def test_admin_with_email():
    """Test d'authentification avec email admin@test.com."""
    print(f"\n📧 TEST AUTHENTIFICATION AVEC EMAIL")
    print("=" * 40)
    
    # Test JWT avec email
    print(f"\n🔐 Test JWT avec email: admin@test.com")
    login_data = {
        "username": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut JWT: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion JWT avec email réussie!")
            print(f"   🔑 Token: {data.get('access', '')[:20]}...")
            print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur JWT avec email: {response.json()}")
    except Exception as e:
        print(f"❌ Exception JWT avec email: {e}")
    
    # Test Token avec email
    print(f"\n🔑 Test Token avec email: admin@test.com")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"📥 Statut Token: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion Token avec email réussie!")
            print(f"   🔑 Token: {data.get('token', '')[:20]}...")
            return True
        else:
            print(f"❌ Erreur Token avec email: {response.json()}")
    except Exception as e:
        print(f"❌ Exception Token avec email: {e}")
    
    return False

def test_protected_endpoints(token, auth_type="JWT"):
    """Test des endpoints protégés avec le token."""
    print(f"\n🔒 TEST ENDPOINTS PROTÉGÉS ({auth_type})")
    print("=" * 45)
    
    if auth_type == "JWT":
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    
    endpoints = [
        ("/entreprises/", "Entreprises"),
        ("/users/", "Utilisateurs"),
        ("/boutiques/", "Boutiques"),
    ]
    
    success_count = 0
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            status = response.status_code
            print(f"   {name}: {status}")
            
            if status == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"      ✅ {name} accessible ({count} éléments)")
                success_count += 1
            elif status == 403:
                print(f"      🚫 {name} accès refusé")
            elif status == 401:
                print(f"      🔒 {name} non authentifié")
            else:
                print(f"      ⚠️  {name} statut: {status}")
                
        except Exception as e:
            print(f"   {name}: ❌ Erreur: {e}")
    
    return success_count

def main():
    print("🚀 TEST AUTHENTIFICATION ADMIN@TEST.COM")
    print("=" * 45)
    
    # 1. Test JWT avec username
    jwt_token, user_id, entreprise_id = test_admin_jwt_auth()
    
    # 2. Test Token avec username
    token_auth = test_admin_token_auth()
    
    # 3. Test avec email
    email_auth_success = test_admin_with_email()
    
    # 4. Test des endpoints protégés
    jwt_endpoints_success = 0
    token_endpoints_success = 0
    
    if jwt_token:
        jwt_endpoints_success = test_protected_endpoints(jwt_token, "JWT")
    
    if token_auth:
        token_endpoints_success = test_protected_endpoints(token_auth, "Token")
    
    # 5. Résumé
    print(f"\n📊 RÉSUMÉ AUTHENTIFICATION ADMIN")
    print("=" * 40)
    print(f"   🔐 JWT avec username: {'✅' if jwt_token else '❌'}")
    print(f"   🔑 Token avec username: {'✅' if token_auth else '❌'}")
    print(f"   📧 Authentification avec email: {'✅' if email_auth_success else '❌'}")
    print(f"   🔒 Endpoints JWT: {jwt_endpoints_success}/3")
    print(f"   🔒 Endpoints Token: {token_endpoints_success}/3")
    
    if jwt_token or token_auth:
        print(f"\n🎉 AUTHENTIFICATION ADMIN FONCTIONNE!")
        print(f"   ✅ Utilisateur: admin@test.com")
        print(f"   ✅ Mot de passe: admin123")
        print(f"   ✅ Username: test")
        
        if jwt_token:
            print(f"   🔐 JWT Token disponible")
        if token_auth:
            print(f"   🔑 Token Auth disponible")
        
        print(f"\n💡 SOLUTION:")
        print(f"   - Utiliser l'username 'test' au lieu de l'email")
        print(f"   - Mot de passe: admin123")
        print(f"   - L'authentification fonctionne avec username")
    else:
        print(f"\n❌ PROBLÈME D'AUTHENTIFICATION")
        print(f"   - Vérifier les identifiants")
        print(f"   - Vérifier la configuration backend")

if __name__ == "__main__":
    main()























































