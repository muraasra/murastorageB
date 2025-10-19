#!/usr/bin/env python3
"""
Vérification des champs API pour s'assurer que les modales affichent tout
- Appel API direct pour voir tous les champs disponibles
- Comparaison avec les champs affichés dans les modales
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

def check_user_api_fields(token, user_id):
    """Vérification des champs API utilisateur."""
    print(f"\n👤 VÉRIFICATION API UTILISATEUR (ID: {user_id})")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 TOUS LES CHAMPS DISPONIBLES DANS L'API:")
            print("-" * 40)
            
            for key, value in data.items():
                print(f"   {key}: {value}")
            
            print(f"\n📊 RÉSUMÉ DES CHAMPS:")
            print(f"   Total: {len(data)} champs")
            print(f"   Champs avec valeurs: {len([k for k, v in data.items() if v is not None and v != ''])}")
            print(f"   Champs vides/null: {len([k for k, v in data.items() if v is None or v == ''])}")
            
            return data
        else:
            print(f"❌ Erreur API: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def check_entreprise_api_fields(token, entreprise_id):
    """Vérification des champs API entreprise."""
    print(f"\n🏢 VÉRIFICATION API ENTREPRISE (ID: {entreprise_id})")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/entreprises/{entreprise_id}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 TOUS LES CHAMPS DISPONIBLES DANS L'API:")
            print("-" * 40)
            
            for key, value in data.items():
                print(f"   {key}: {value}")
            
            print(f"\n📊 RÉSUMÉ DES CHAMPS:")
            print(f"   Total: {len(data)} champs")
            print(f"   Champs avec valeurs: {len([k for k, v in data.items() if v is not None and v != ''])}")
            print(f"   Champs vides/null: {len([k for k, v in data.items() if v is None or v == ''])}")
            
            return data
        else:
            print(f"❌ Erreur API: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def check_user_serializer_fields():
    """Vérification des champs du serializer User."""
    print(f"\n🔍 VÉRIFICATION SERIALIZER USER")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/users/", headers={})
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                user_fields = list(data[0].keys())
                print(f"\n📋 CHAMPS DU SERIALIZER USER:")
                print("-" * 30)
                for field in user_fields:
                    print(f"   ✅ {field}")
                return user_fields
        else:
            print(f"❌ Erreur: {response.json()}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def check_entreprise_serializer_fields():
    """Vérification des champs du serializer Entreprise."""
    print(f"\n🔍 VÉRIFICATION SERIALIZER ENTREPRISE")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/entreprises/", headers={})
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                entreprise_fields = list(data[0].keys())
                print(f"\n📋 CHAMPS DU SERIALIZER ENTREPRISE:")
                print("-" * 30)
                for field in entreprise_fields:
                    print(f"   ✅ {field}")
                return entreprise_fields
        else:
            print(f"❌ Erreur: {response.json()}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def compare_modal_vs_api():
    """Comparaison des champs modales vs API."""
    print(f"\n🔍 COMPARAISON MODALES VS API")
    print("=" * 50)
    
    # Champs affichés dans EditProfileModal.vue
    modal_profile_fields = [
        'first_name', 'last_name', 'email', 'telephone', 
        'poste', 'date_embauche', 'password', 'confirm_password'
    ]
    
    # Champs affichés dans EditEntrepriseModal.vue
    modal_entreprise_fields = [
        'nom', 'secteur_activite', 'ville', 'code_postal', 'pays',
        'telephone', 'email', 'site_web', 'pack_type', 'nombre_employes',
        'annee_creation', 'numero_fiscal', 'adresse'
    ]
    
    print(f"\n👤 CHAMPS MODAL PROFIL:")
    print("-" * 25)
    for field in modal_profile_fields:
        print(f"   ✅ {field}")
    
    print(f"\n🏢 CHAMPS MODAL ENTREPRISE:")
    print("-" * 30)
    for field in modal_entreprise_fields:
        print(f"   ✅ {field}")

def main():
    print("🚀 VÉRIFICATION DES CHAMPS API")
    print("=" * 50)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Vérification des champs API
    user_data = check_user_api_fields(access_token, user_id)
    entreprise_data = check_entreprise_api_fields(access_token, entreprise_id)
    
    # 3. Vérification des serializers
    user_serializer_fields = check_user_serializer_fields()
    entreprise_serializer_fields = check_entreprise_serializer_fields()
    
    # 4. Comparaison modales vs API
    compare_modal_vs_api()
    
    # 5. Analyse des différences
    print(f"\n📊 ANALYSE DES DIFFÉRENCES")
    print("=" * 35)
    
    if user_data:
        api_user_fields = set(user_data.keys())
        modal_user_fields = {'first_name', 'last_name', 'email', 'telephone', 'poste', 'date_embauche'}
        
        missing_in_modal = api_user_fields - modal_user_fields
        extra_in_modal = modal_user_fields - api_user_fields
        
        print(f"\n👤 UTILISATEUR:")
        print(f"   Champs API: {len(api_user_fields)}")
        print(f"   Champs Modal: {len(modal_user_fields)}")
        if missing_in_modal:
            print(f"   ❌ Manquants dans modal: {missing_in_modal}")
        if extra_in_modal:
            print(f"   ⚠️  Extra dans modal: {extra_in_modal}")
        if not missing_in_modal and not extra_in_modal:
            print(f"   ✅ Tous les champs sont présents")
    
    if entreprise_data:
        api_entreprise_fields = set(entreprise_data.keys())
        modal_entreprise_fields = {'nom', 'secteur_activite', 'ville', 'code_postal', 'pays', 'telephone', 'email', 'site_web', 'pack_type', 'nombre_employes', 'annee_creation', 'numero_fiscal', 'adresse'}
        
        missing_in_modal = api_entreprise_fields - modal_entreprise_fields
        extra_in_modal = modal_entreprise_fields - api_entreprise_fields
        
        print(f"\n🏢 ENTREPRISE:")
        print(f"   Champs API: {len(api_entreprise_fields)}")
        print(f"   Champs Modal: {len(modal_entreprise_fields)}")
        if missing_in_modal:
            print(f"   ❌ Manquants dans modal: {missing_in_modal}")
        if extra_in_modal:
            print(f"   ⚠️  Extra dans modal: {extra_in_modal}")
        if not missing_in_modal and not extra_in_modal:
            print(f"   ✅ Tous les champs sont présents")

if __name__ == "__main__":
    main()































