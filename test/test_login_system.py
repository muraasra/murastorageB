#!/usr/bin/env python3
"""
Test du système de connexion et dashboard SuperAdmin
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_jwt_login():
    """Test de la connexion JWT"""
    print("🔐 Test de connexion JWT...")
    
    # Données de test (utiliser un utilisateur existant)
    login_data = {
        "username": "admin@test.com",  # Remplacer par un email existant
        "password": "admin123"  # Remplacer par le mot de passe correct
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"   Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Connexion réussie!")
            print(f"   👤 Utilisateur: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'Aucune')}")
            print(f"   🏪 Boutique: {data.get('boutique', {}).get('nom', 'Aucune')}")
            print(f"   🔑 Token: {data.get('access', '')[:20]}...")
            return data.get('access')
        else:
            print(f"   ❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_create_boutique(token):
    """Test de création d'entrepôt"""
    print("\n🏪 Test de création d'entrepôt...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    boutique_data = {
        "nom": f"Entrepôt Test {int(time.time())}",
        "ville": "Douala",
        "responsable": "Responsable Test",
        "adresse": "Adresse test, Douala",
        "telephone": "+237 6XX XXX XXX"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/boutiques/", json=boutique_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Entrepôt créé: {data.get('nom')} (ID: {data.get('id')})")
            return data.get('id')
        else:
            print(f"   ❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_create_user(token, boutique_id):
    """Test de création d'utilisateur avec envoi d'email"""
    print("\n👤 Test de création d'utilisateur...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    user_data = {
        "username": f"testuser{int(time.time())}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser{int(time.time())}@example.com",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Gestionnaire de stock",
        "role": "user",
        "boutique": boutique_id,
        "send_email": True  # Activer l'envoi d'email
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Utilisateur créé: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            print(f"   📧 Email envoyé: {data.get('email_sent', False)}")
            if data.get('temp_password'):
                print(f"   🔑 Mot de passe temporaire: {data.get('temp_password')}")
            return data.get('user', {}).get('id')
        else:
            print(f"   ❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_get_stats(token):
    """Test de récupération des statistiques"""
    print("\n📊 Test des statistiques...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test récupération entrepôts
        response = requests.get(f"{BASE_URL}/boutiques/", headers=headers)
        if response.status_code == 200:
            boutiques = response.json()
            print(f"   🏪 Entrepôts: {len(boutiques)}")
        
        # Test récupération utilisateurs
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   👤 Utilisateurs: {len(users)}")
        
        # Test récupération produits
        response = requests.get(f"{BASE_URL}/produits/", headers=headers)
        if response.status_code == 200:
            produits = response.json()
            print(f"   📦 Produits: {len(produits)}")
        
        # Test récupération factures
        response = requests.get(f"{BASE_URL}/factures/", headers=headers)
        if response.status_code == 200:
            factures = response.json()
            print(f"   🧾 Factures: {len(factures)}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Test du système de connexion et dashboard SuperAdmin")
    print("=" * 60)
    
    # 1. Test de connexion
    token = test_jwt_login()
    if not token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return
    
    # 2. Test des statistiques
    test_get_stats(token)
    
    # 3. Test de création d'entrepôt
    boutique_id = test_create_boutique(token)
    
    # 4. Test de création d'utilisateur (si entrepôt créé)
    if boutique_id:
        test_create_user(token, boutique_id)
    
    print("\n✅ Tests terminés!")
    print("\n📝 Notes:")
    print("   - Vérifiez votre boîte email pour l'email de création d'utilisateur")
    print("   - Testez la page de connexion frontend avec les identifiants")
    print("   - Explorez le dashboard SuperAdmin")

if __name__ == "__main__":
    main()
