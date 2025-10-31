#!/usr/bin/env python3
"""
Test avec les données exactes du frontend
- Tester avec des valeurs vides, null, undefined
- Tester avec des types incorrects
- Identifier le problème spécifique
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "admin@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT et récupération du token."""
    print("🔐 Connexion JWT...")
    login_data = {
        "username": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data['access'], data['user']['id'], data['entreprise']['id']
        else:
            print(f"❌ Erreur connexion: {response.json()}")
            return None, None, None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, None, None

def test_frontend_data_scenarios(token, user_id):
    """Tester différents scénarios de données frontend."""
    print(f"\n🧪 TEST SCÉNARIOS DONNÉES FRONTEND")
    print("=" * 45)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Scénario 1: Données avec valeurs vides (comme dans le frontend)
    print(f"\n📝 Scénario 1: Valeurs vides")
    empty_data = {
        "first_name": "",
        "last_name": "",
        "telephone": "",
        "poste": "",
        "date_embauche": "",
        "is_active_employee": True
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=empty_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Scénario 2: Données avec null (JavaScript null)
    print(f"\n📝 Scénario 2: Valeurs null")
    null_data = {
        "first_name": None,
        "last_name": None,
        "telephone": None,
        "poste": None,
        "date_embauche": None,
        "is_active_employee": True
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=null_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Scénario 3: Données avec types incorrects
    print(f"\n📝 Scénario 3: Types incorrects")
    wrong_type_data = {
        "first_name": 123,
        "last_name": 456,
        "telephone": 789,
        "poste": 101112,
        "date_embauche": 2023,  # Nombre au lieu de string
        "is_active_employee": "true"  # String au lieu de boolean
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=wrong_type_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Scénario 4: Données avec champs manquants
    print(f"\n📝 Scénario 4: Champs manquants")
    missing_data = {
        "first_name": "Test"
        # Pas de last_name, telephone, etc.
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=missing_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Scénario 5: Données avec champs supplémentaires
    print(f"\n📝 Scénario 5: Champs supplémentaires")
    extra_data = {
        "first_name": "Test",
        "last_name": "Test",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Test",
        "date_embauche": "2023-01-15",
        "is_active_employee": True,
        "username": "test",  # Champ non modifiable
        "role": "superadmin",  # Champ non modifiable
        "entreprise": 10,  # Champ non modifiable
        "boutique": 9  # Champ non modifiable
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=extra_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_user_model_validation():
    """Tester la validation du modèle User."""
    print(f"\n🔍 TEST VALIDATION MODÈLE USER")
    print("=" * 35)
    
    # Vérifier les champs requis du modèle User Django
    required_fields = ['username', 'email']
    optional_fields = ['first_name', 'last_name', 'telephone', 'poste', 'date_embauche', 'is_active_employee']
    
    print(f"📋 Champs requis: {required_fields}")
    print(f"📋 Champs optionnels: {optional_fields}")
    
    # Test avec des données valides mais minimales
    print(f"\n📝 Test données minimales valides")
    minimal_valid_data = {
        "first_name": "Test",
        "last_name": "Test"
    }
    
    return required_fields, optional_fields

def test_serializer_validation():
    """Tester la validation du serializer."""
    print(f"\n🔍 TEST VALIDATION SERIALIZER")
    print("=" * 35)
    
    # Vérifier les champs du serializer UserSerializer
    serializer_fields = [
        'id', 'username', 'email', 'first_name', 'last_name', 'role', 
        'entreprise', 'boutique', 'telephone', 'poste', 'date_embauche', 
        'is_active_employee', 'created_at', 'updated_at',
        'entreprise_nom', 'boutique_nom'
    ]
    
    read_only_fields = ['created_at', 'updated_at']
    
    print(f"📋 Champs serializer: {len(serializer_fields)}")
    print(f"📋 Champs read-only: {read_only_fields}")
    
    return serializer_fields, read_only_fields

def main():
    print("🚀 TEST DONNÉES FRONTEND EXACTES")
    print("=" * 40)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Tests avec différents scénarios
    test_frontend_data_scenarios(access_token, user_id)
    
    # 3. Tests de validation
    required_fields, optional_fields = test_user_model_validation()
    serializer_fields, read_only_fields = test_serializer_validation()
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    print(f"   📋 Champs requis: {len(required_fields)}")
    print(f"   📋 Champs optionnels: {len(optional_fields)}")
    print(f"   📋 Champs serializer: {len(serializer_fields)}")
    print(f"   📋 Champs read-only: {len(read_only_fields)}")
    
    print(f"\n🔍 DIAGNOSTIC:")
    print(f"   - Vérifier les logs du navigateur")
    print(f"   - Vérifier les données envoyées par le frontend")
    print(f"   - Vérifier les types de données")
    print(f"   - Vérifier les champs requis")

if __name__ == "__main__":
    main()























































