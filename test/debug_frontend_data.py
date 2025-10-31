#!/usr/bin/env python3
"""
Script pour déboguer les données envoyées par le frontend
- Vérifier la structure des données
- Identifier les champs manquants
- Corriger les erreurs 400
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "admin@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT et récupération du token."""
    print("🔐 Test de connexion JWT...")
    login_data = {
        "username": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Connexion réussie!")
            print(f"   👤 Utilisateur: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   🏢 Entreprise: {data['entreprise']['nom']}")
            print(f"   🏪 Boutique: {data['boutique']['nom']}")
            print(f"   🔑 Token: {data['access'][:20]}...")
            return data['access'], data['user']['id'], data['entreprise']['id'], data['boutique']['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None, None, None, None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None, None, None, None

def test_user_update_structure(token, user_id):
    """Test de la structure des données pour la mise à jour utilisateur."""
    print(f"\n👤 Test de la structure des données utilisateur...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Structure exacte que le frontend devrait envoyer
    update_data = {
        "username": SUPERADMIN_EMAIL,  # Requis
        "first_name": "Admin Frontend",
        "last_name": "Test Frontend", 
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Frontend",
        "date_embauche": "2023-01-15",
        "role": "superadmin"  # Requis
    }
    
    print(f"   📤 Données envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Utilisateur mis à jour avec succès")
            print(f"      Nom: {data['first_name']} {data['last_name']}")
            print(f"      Email: {data['email']}")
            print(f"      Rôle: {data['role']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_entreprise_update_structure(token, entreprise_id):
    """Test de la structure des données pour la mise à jour entreprise."""
    print(f"\n🏢 Test de la structure des données entreprise...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Structure exacte que le frontend devrait envoyer
    update_data = {
        "nom": "Entreprise Frontend Test",
        "secteur_activite": "technologie",
        "ville": "Douala Frontend",
        "code_postal": "00237",
        "pays": "Cameroun",
        "telephone": "+237 6XX XXX XXX",
        "email": "contact@frontend.com",
        "site_web": "https://www.frontend.com",
        "pack_type": "professionnel",
        "nombre_employes": 25,
        "annee_creation": 2023,
        "numero_fiscal": "F123456789",
        "adresse": "123 Rue Frontend, Douala, Cameroun"
    }
    
    print(f"   📤 Données envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.put(f"{BASE_URL}/entreprises/{entreprise_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Entreprise mise à jour avec succès")
            print(f"      Nom: {data['nom']}")
            print(f"      Secteur: {data['secteur_activite']}")
            print(f"      Ville: {data['ville']}")
            print(f"      Pack: {data['pack_type']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_user_fields_validation(token, user_id):
    """Test de validation des champs utilisateur."""
    print(f"\n🔍 Test de validation des champs utilisateur...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test avec champs manquants
    test_cases = [
        {
            "name": "Sans username",
            "data": {
                "first_name": "Test",
                "last_name": "User",
                "role": "superadmin"
            }
        },
        {
            "name": "Sans role", 
            "data": {
                "username": SUPERADMIN_EMAIL,
                "first_name": "Test",
                "last_name": "User"
            }
        },
        {
            "name": "Sans first_name",
            "data": {
                "username": SUPERADMIN_EMAIL,
                "last_name": "User",
                "role": "superadmin"
            }
        },
        {
            "name": "Sans last_name",
            "data": {
                "username": SUPERADMIN_EMAIL,
                "first_name": "Test",
                "role": "superadmin"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"   🧪 Test: {test_case['name']}")
        try:
            response = requests.put(f"{BASE_URL}/users/{user_id}/", json=test_case['data'], headers=headers)
            print(f"      Statut: {response.status_code}")
            if response.status_code == 400:
                print(f"      ❌ Erreur attendue: {response.json()}")
            else:
                print(f"      ⚠️  Statut inattendu: {response.json()}")
        except Exception as e:
            print(f"      ❌ Erreur: {e}")

def test_entreprise_fields_validation(token, entreprise_id):
    """Test de validation des champs entreprise."""
    print(f"\n🔍 Test de validation des champs entreprise...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test avec champs manquants
    test_cases = [
        {
            "name": "Sans nom",
            "data": {
                "secteur_activite": "technologie",
                "ville": "Douala",
                "email": "test@test.com",
                "annee_creation": 2023
            }
        },
        {
            "name": "Sans ville",
            "data": {
                "nom": "Test Entreprise",
                "secteur_activite": "technologie", 
                "email": "test@test.com",
                "annee_creation": 2023
            }
        },
        {
            "name": "Sans email",
            "data": {
                "nom": "Test Entreprise",
                "secteur_activite": "technologie",
                "ville": "Douala",
                "annee_creation": 2023
            }
        },
        {
            "name": "Sans annee_creation",
            "data": {
                "nom": "Test Entreprise",
                "secteur_activite": "technologie",
                "ville": "Douala",
                "email": "test@test.com"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"   🧪 Test: {test_case['name']}")
        try:
            response = requests.put(f"{BASE_URL}/entreprises/{entreprise_id}/", json=test_case['data'], headers=headers)
            print(f"      Statut: {response.status_code}")
            if response.status_code == 400:
                print(f"      ❌ Erreur attendue: {response.json()}")
            else:
                print(f"      ⚠️  Statut inattendu: {response.json()}")
        except Exception as e:
            print(f"      ❌ Erreur: {e}")

def main():
    print("🚀 Debug des données frontend")
    print("=" * 50)

    # 1. Connexion
    access_token, user_id, entreprise_id, boutique_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    # 2. Test structure des données
    test_user_update_structure(access_token, user_id)
    test_entreprise_update_structure(access_token, entreprise_id)
    
    # 3. Test validation des champs
    test_user_fields_validation(access_token, user_id)
    test_entreprise_fields_validation(access_token, entreprise_id)

    print("\n✅ Debug terminé!")
    print("\n📝 Résumé:")
    print("   ✅ Structure des données vérifiée")
    print("   ✅ Champs requis identifiés")
    print("   ✅ Validation des champs testée")

if __name__ == "__main__":
    main()























































