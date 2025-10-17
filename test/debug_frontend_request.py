#!/usr/bin/env python3
"""
Debug de la requête frontend exacte
- Simuler exactement ce que le frontend envoie
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

def debug_user_patch_exact(token, user_id):
    """Debug exact de la requête PATCH utilisateur."""
    print(f"\n👤 DEBUG PATCH UTILISATEUR EXACT (ID: {user_id})")
    print("=" * 55)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données exactes comme dans le frontend
    patch_data = {
        "first_name": "Admin Frontend",
        "last_name": "Test Frontend", 
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Frontend",
        "date_embauche": "2023-01-15",
        "is_active_employee": True
    }
    
    print(f"📤 Headers:")
    for key, value in headers.items():
        if key == "Authorization":
            print(f"   {key}: Bearer {value[7:20]}...")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n📤 Body (JSON):")
    print(json.dumps(patch_data, indent=2))
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        print(f"📥 Headers de réponse:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Succès!")
            print(f"   👨 Nom: {data.get('first_name')} {data.get('last_name')}")
            return True
        else:
            print(f"\n❌ Erreur {response.status_code}")
            print(f"📥 Contenu de la réponse:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_user_serializer_fields():
    """Tester les champs du serializer User."""
    print(f"\n🔍 TEST SERIALIZER USER")
    print("=" * 30)
    
    try:
        # Test avec des données minimales
        response = requests.get(f"{BASE_URL}/users/", headers={})
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                user_fields = list(data[0].keys())
                print(f"✅ Champs disponibles dans l'API:")
                for field in user_fields:
                    print(f"   - {field}")
                return user_fields
        else:
            print(f"❌ Erreur: {response.json()}")
            return []
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def test_user_model_fields():
    """Tester les champs du modèle User."""
    print(f"\n🔍 TEST MODÈLE USER")
    print("=" * 25)
    
    # Champs typiques d'un modèle User Django
    expected_fields = [
        'id', 'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined',
        'last_login', 'groups', 'user_permissions'
    ]
    
    print(f"📋 Champs attendus dans le modèle User:")
    for field in expected_fields:
        print(f"   - {field}")
    
    return expected_fields

def test_user_patch_with_different_data(token, user_id):
    """Tester PATCH avec différentes données."""
    print(f"\n🧪 TEST PATCH AVEC DIFFÉRENTES DONNÉES")
    print("=" * 45)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Données minimales
    print(f"\n📝 Test 1: Données minimales")
    minimal_data = {"first_name": "Test Minimal"}
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=minimal_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Données avec champs vides
    print(f"\n📝 Test 2: Champs vides")
    empty_data = {
        "first_name": "",
        "last_name": "",
        "telephone": "",
        "poste": ""
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=empty_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Données avec types incorrects
    print(f"\n📝 Test 3: Types incorrects")
    wrong_type_data = {
        "first_name": 123,  # Nombre au lieu de string
        "is_active_employee": "true"  # String au lieu de boolean
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=wrong_type_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code != 200:
            print(f"   Erreur: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def main():
    print("🚀 DEBUG REQUÊTE FRONTEND EXACTE")
    print("=" * 40)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Debug de la requête exacte
    success = debug_user_patch_exact(access_token, user_id)
    
    # 3. Test des champs du serializer
    serializer_fields = test_user_serializer_fields()
    
    # 4. Test des champs du modèle
    model_fields = test_user_model_fields()
    
    # 5. Tests avec différentes données
    test_user_patch_with_different_data(access_token, user_id)
    
    # 6. Résumé
    print(f"\n📊 RÉSUMÉ DU DEBUG")
    print("=" * 25)
    print(f"   🔍 Requête exacte: {'✅' if success else '❌'}")
    print(f"   📋 Champs serializer: {len(serializer_fields)}")
    print(f"   📋 Champs modèle: {len(model_fields)}")
    
    if not success:
        print(f"\n🔍 DIAGNOSTIC:")
        print(f"   - Vérifier les permissions utilisateur")
        print(f"   - Vérifier les validations du serializer")
        print(f"   - Vérifier les champs requis")
        print(f"   - Vérifier les types de données")

if __name__ == "__main__":
    main()




























