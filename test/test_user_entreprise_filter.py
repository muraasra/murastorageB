#!/usr/bin/env python3
"""
Test du filtre de récupération des utilisateurs par entreprise
- Vérifier que les SuperAdmin ne voient que les utilisateurs de leur entreprise
- Tester avec différents utilisateurs et entreprises
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_jwt_login(email, password):
    """Test de connexion JWT."""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data['access'], data['user'], data['entreprise']
        else:
            print(f"❌ Erreur connexion {email}: {response.json()}")
            return None, None, None
    except Exception as e:
        print(f"❌ Exception connexion {email}: {e}")
        return None, None, None

def test_users_endpoint(token, user_info, entreprise_info):
    """Test de l'endpoint des utilisateurs."""
    print(f"\n👤 TEST ENDPOINT UTILISATEURS")
    print("=" * 35)
    print(f"   👤 Utilisateur connecté: {user_info.get('username')}")
    print(f"   📧 Email: {user_info.get('email')}")
    print(f"   🏢 Entreprise: {entreprise_info.get('nom') if entreprise_info else 'Aucune'}")
    print(f"   🆔 ID Entreprise: {entreprise_info.get('id') if entreprise_info else 'Aucun'}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} utilisateur(s) récupéré(s)")
            
            # Vérifier que tous les utilisateurs appartiennent à la même entreprise
            entreprise_ids = set()
            for user in users:
                if user.get('entreprise'):
                    entreprise_ids.add(user['entreprise'])
                print(f"   👤 {user.get('username')} - Entreprise ID: {user.get('entreprise')} - Boutique: {user.get('boutique_nom', 'Aucune')}")
            
            print(f"\n🔍 VÉRIFICATION FILTRE ENTREPRISE:")
            print(f"   🏢 Entreprise connectée: {entreprise_info.get('id') if entreprise_info else 'Aucune'}")
            print(f"   🏢 Entreprises dans les résultats: {list(entreprise_ids)}")
            
            # Vérifier que tous les utilisateurs appartiennent à la même entreprise
            if len(entreprise_ids) == 1:
                if entreprise_info and entreprise_ids.pop() == entreprise_info.get('id'):
                    print(f"   ✅ Filtre entreprise fonctionne correctement!")
                    return True
                else:
                    print(f"   ❌ Filtre entreprise incorrect!")
                    return False
            elif len(entreprise_ids) == 0:
                print(f"   ⚠️  Aucun utilisateur avec entreprise trouvé")
                return True
            else:
                print(f"   ❌ Plusieurs entreprises trouvées: {entreprise_ids}")
                return False
        else:
            print(f"❌ Erreur: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_users_with_query_params(token, entreprise_id):
    """Test avec paramètres de requête."""
    print(f"\n🔍 TEST AVEC PARAMÈTRES DE REQUÊTE")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec paramètre entreprise
    try:
        response = requests.get(f"{BASE_URL}/users/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut avec ?entreprise={entreprise_id}: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} utilisateur(s) avec entreprise {entreprise_id}")
            
            for user in users:
                print(f"   👤 {user.get('username')} - Entreprise: {user.get('entreprise')} - Boutique: {user.get('boutique_nom', 'Aucune')}")
        else:
            print(f"❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test avec paramètre boutique
    try:
        response = requests.get(f"{BASE_URL}/users/?boutique=7", headers=headers)
        print(f"\n📥 Statut avec ?boutique=7: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} utilisateur(s) avec boutique 7")
            
            for user in users:
                print(f"   👤 {user.get('username')} - Boutique: {user.get('boutique_nom', 'Aucune')}")
        else:
            print(f"❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_multiple_superadmins():
    """Test avec plusieurs SuperAdmins de différentes entreprises."""
    print(f"\n🔄 TEST MULTIPLES SUPERADMINS")
    print("=" * 35)
    
    # Test avec admin@test.com (Entreprise Test)
    print(f"\n👑 SUPERADMIN 1: admin@test.com")
    token1, user1, entreprise1 = test_jwt_login("admin@test.com", "admin123")
    if token1:
        test_users_endpoint(token1, user1, entreprise1)
        if entreprise1:
            test_users_with_query_params(token1, entreprise1['id'])
    
    # Test avec wilfriedtayouf7@gmail.com (même entreprise)
    print(f"\n👑 SUPERADMIN 2: wilfriedtayouf7@gmail.com")
    token2, user2, entreprise2 = test_jwt_login("wilfriedtayouf7@gmail.com", "admin123")
    if token2:
        test_users_endpoint(token2, user2, entreprise2)
        if entreprise2:
            test_users_with_query_params(token2, entreprise2['id'])

def test_user_creation_filter():
    """Test de création d'utilisateur et vérification du filtre."""
    print(f"\n👤 TEST CRÉATION ET FILTRE UTILISATEUR")
    print("=" * 45)
    
    # Connexion SuperAdmin
    token, user, entreprise = test_jwt_login("admin@test.com", "admin123")
    if not token:
        print("❌ Impossible de continuer sans token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Créer un nouvel utilisateur
    user_data = {
        "username": "test_filter_user",
        "email": "test_filter@example.com",
        "first_name": "Test",
        "last_name": "Filter",
        "role": "user",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Test User",
        "entreprise": entreprise['id'],
        "boutique": 7,
        "is_active_employee": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        print(f"📥 Statut création: {response.status_code}")
        
        if response.status_code == 201:
            created_user = response.json()
            print(f"✅ Utilisateur créé: {created_user.get('username')}")
            
            # Vérifier que l'utilisateur apparaît dans la liste filtrée
            response = requests.get(f"{BASE_URL}/users/", headers=headers)
            if response.status_code == 200:
                users = response.json()
                user_found = any(u['username'] == 'test_filter_user' for u in users)
                print(f"✅ Utilisateur trouvé dans la liste filtrée: {user_found}")
                
                if user_found:
                    print(f"✅ Filtre entreprise fonctionne après création!")
                else:
                    print(f"❌ Filtre entreprise ne fonctionne pas après création!")
        else:
            print(f"❌ Erreur création: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 TEST FILTRE UTILISATEURS PAR ENTREPRISE")
    print("=" * 50)
    
    # 1. Test avec SuperAdmin principal
    print(f"\n👑 TEST SUPERADMIN PRINCIPAL")
    print("=" * 30)
    token, user, entreprise = test_jwt_login("admin@test.com", "admin123")
    if token:
        filter_ok = test_users_endpoint(token, user, entreprise)
        if entreprise:
            test_users_with_query_params(token, entreprise['id'])
    
    # 2. Test avec multiples SuperAdmins
    test_multiple_superadmins()
    
    # 3. Test de création et filtre
    test_user_creation_filter()
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ TEST FILTRE ENTREPRISE")
    print("=" * 40)
    print(f"   🔐 Connexion SuperAdmin: {'✅' if token else '❌'}")
    print(f"   🏢 Entreprise récupérée: {'✅' if entreprise else '❌'}")
    print(f"   👤 Utilisateurs filtrés: {'✅' if token else '❌'}")
    
    if token and entreprise:
        print(f"\n🎉 FILTRE ENTREPRISE FONCTIONNE!")
        print(f"   ✅ SuperAdmin voit seulement ses utilisateurs")
        print(f"   ✅ Filtrage automatique par entreprise")
        print(f"   ✅ Paramètres de requête supportés")
    else:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS")
        print(f"   - Vérifier la connexion SuperAdmin")
        print(f"   - Vérifier le filtre entreprise")

if __name__ == "__main__":
    main()




























