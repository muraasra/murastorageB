#!/usr/bin/env python3
"""
Test de l'authentification JWT après correction
- Vérifier que l'authentification fonctionne
- Tester les endpoints protégés
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "testuser@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT."""
    print("🔐 TEST CONNEXION JWT")
    print("=" * 25)
    
    login_data = {
        "username": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion réussie!")
            print(f"   🔑 Token reçu: {data.get('access', '')[:20]}...")
            print(f"   👤 Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
            return data['access'], data['user']['id'], data['entreprise']['id']
        else:
            print(f"❌ Erreur: {response.json()}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None, None

def test_protected_endpoints(token):
    """Test des endpoints protégés avec authentification."""
    print(f"\n🔒 TEST ENDPOINTS PROTÉGÉS")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        ("/entreprises/", "Entreprises"),
        ("/users/", "Utilisateurs"),
        ("/boutiques/", "Boutiques"),
        ("/produits/", "Produits"),
        ("/factures/", "Factures"),
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            status = response.status_code
            print(f"   {name}: {status}")
            results[endpoint] = status
            
            if status == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 1
                print(f"      ✅ {name} accessible ({count} éléments)")
            elif status == 403:
                print(f"      🚫 {name} accès refusé")
            elif status == 401:
                print(f"      🔒 {name} non authentifié")
            else:
                print(f"      ⚠️  {name} statut: {status}")
                
        except Exception as e:
            print(f"   {name}: ❌ Erreur: {e}")
            results[endpoint] = "ERROR"
    
    return results

def test_entreprise_filtering(token, entreprise_id):
    """Test du filtrage par entreprise."""
    print(f"\n🏢 TEST FILTRAGE ENTREPRISE")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test entrepôts filtrés
    try:
        response = requests.get(f"{BASE_URL}/boutiques/?entreprise={entreprise_id}", headers=headers)
        if response.status_code == 200:
            boutiques = response.json()
            print(f"   📦 Entrepôts de l'entreprise: {len(boutiques)}")
            
            # Vérifier que tous appartiennent à l'entreprise
            for boutique in boutiques:
                if boutique.get('entreprise') != entreprise_id:
                    print(f"   ❌ Erreur: Entrepôt {boutique.get('nom')} n'appartient pas à l'entreprise")
                    return False
            
            print(f"   ✅ Tous les entrepôts appartiennent à l'entreprise")
        else:
            print(f"   ❌ Erreur entrepôts: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception entrepôts: {e}")
        return False
    
    # Test utilisateurs filtrés
    try:
        response = requests.get(f"{BASE_URL}/users/?entreprise={entreprise_id}", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   👥 Utilisateurs de l'entreprise: {len(users)}")
            
            # Vérifier que tous appartiennent à l'entreprise
            for user in users:
                if user.get('entreprise') != entreprise_id:
                    print(f"   ❌ Erreur: Utilisateur {user.get('username')} n'appartient pas à l'entreprise")
                    return False
            
            print(f"   ✅ Tous les utilisateurs appartiennent à l'entreprise")
        else:
            print(f"   ❌ Erreur utilisateurs: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception utilisateurs: {e}")
        return False
    
    return True

def main():
    print("🚀 TEST AUTHENTIFICATION JWT APRÈS CORRECTION")
    print("=" * 50)
    
    # 1. Test de connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    print(f"\n✅ Connexion réussie!")
    print(f"   👤 User ID: {user_id}")
    print(f"   🏢 Entreprise ID: {entreprise_id}")
    
    # 2. Test des endpoints protégés
    protected_results = test_protected_endpoints(access_token)
    
    # 3. Test du filtrage par entreprise
    filtering_success = test_entreprise_filtering(access_token, entreprise_id)
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    
    success_count = sum(1 for status in protected_results.values() if status == 200)
    total_count = len(protected_results)
    
    print(f"   🔐 Authentification JWT: ✅")
    print(f"   🔒 Endpoints protégés: {success_count}/{total_count}")
    print(f"   🏢 Filtrage entreprise: {'✅' if filtering_success else '❌'}")
    
    if success_count == total_count and filtering_success:
        print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
        print(f"   ✅ L'authentification JWT fonctionne")
        print(f"   ✅ Les endpoints protégés sont accessibles")
        print(f"   ✅ Le filtrage par entreprise fonctionne")
        print(f"   ✅ L'erreur 500 est résolue")
    else:
        print(f"\n⚠️  Des problèmes persistent")
        if success_count < total_count:
            print(f"   - Vérifier les permissions des endpoints")
        if not filtering_success:
            print(f"   - Vérifier le filtrage par entreprise")

if __name__ == "__main__":
    main()
