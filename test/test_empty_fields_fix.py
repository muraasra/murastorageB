#!/usr/bin/env python3
"""
Test de la correction des champs vides
- Vérifier que les champs vides ne causent plus d'erreurs 400
- Tester avec des données partielles
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

def test_profile_patch_with_empty_fields(token, user_id):
    """Test PATCH profil avec champs vides (comme le frontend corrigé)."""
    print(f"\n👤 TEST PATCH PROFIL AVEC CHAMPS VIDES")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Données partielles (comme le frontend corrigé)
    print(f"\n📝 Test 1: Données partielles")
    partial_data = {
        "first_name": "Admin Test",
        "last_name": "PATCH Test"
        # Pas de telephone, poste, date_embauche
    }
    
    print(f"📤 Données envoyées:")
    for key, value in partial_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=partial_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   👨 Nom: {data.get('first_name')} {data.get('last_name')}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data}")
            except:
                print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_profile_patch_with_some_empty_fields(token, user_id):
    """Test PATCH profil avec certains champs vides."""
    print(f"\n📝 Test 2: Certains champs vides")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec des champs vides mais valides
    empty_fields_data = {
        "first_name": "Admin Empty",
        "last_name": "Test Empty",
        "telephone": "",  # Champ vide
        "poste": "",      # Champ vide
        "date_embauche": "",  # Champ vide
        "is_active_employee": True
    }
    
    print(f"📤 Données avec champs vides:")
    for key, value in empty_fields_data.items():
        print(f"   {key}: '{value}'")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=empty_fields_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès avec champs vides!")
            print(f"   👨 Nom: {data.get('first_name')} {data.get('last_name')}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data}")
            except:
                print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_entreprise_patch_with_empty_fields(token, entreprise_id):
    """Test PATCH entreprise avec champs vides."""
    print(f"\n🏢 TEST PATCH ENTREPRISE AVEC CHAMPS VIDES")
    print("=" * 55)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec des données partielles
    partial_data = {
        "nom": "Entreprise Test Empty",
        "ville": "Douala Test"
        # Pas d'autres champs
    }
    
    print(f"📤 Données partielles:")
    for key, value in partial_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=partial_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   🏢 Nom: {data.get('nom')}")
            print(f"   🏙️ Ville: {data.get('ville')}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data}")
            except:
                print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_entreprise_patch_with_some_empty_fields(token, entreprise_id):
    """Test PATCH entreprise avec certains champs vides."""
    print(f"\n📝 Test entreprise avec champs vides")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec des champs vides
    empty_fields_data = {
        "nom": "Entreprise Empty Test",
        "description": "",  # Champ vide
        "secteur_activite": "technologie",
        "ville": "Douala Empty",
        "code_postal": "",  # Champ vide
        "pays": "Cameroun",
        "telephone": "",    # Champ vide
        "email": "contact@empty.com",
        "site_web": "",     # Champ vide
        "pack_type": "basique",
        "nombre_employes": 0,
        "annee_creation": 2023,
        "numero_fiscal": "",  # Champ vide
        "pack_prix": 0,
        "pack_duree": "mensuel",
        "is_active": True,
        "adresse": "123 Rue Empty, Douala, Cameroun"
    }
    
    print(f"📤 Données avec champs vides:")
    for key, value in empty_fields_data.items():
        if value == "":
            print(f"   {key}: '[VIDE]'")
        else:
            print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=empty_fields_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès avec champs vides!")
            print(f"   🏢 Nom: {data.get('nom')}")
            print(f"   🏙️ Ville: {data.get('ville')}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data}")
            except:
                print(f"   Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 TEST CORRECTION CHAMPS VIDES")
    print("=" * 35)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Tests profil
    profile_success1 = test_profile_patch_with_empty_fields(access_token, user_id)
    profile_success2 = test_profile_patch_with_some_empty_fields(access_token, user_id)
    
    # 3. Tests entreprise
    entreprise_success1 = test_entreprise_patch_with_empty_fields(access_token, entreprise_id)
    entreprise_success2 = test_entreprise_patch_with_some_empty_fields(access_token, entreprise_id)
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    print(f"   👤 PATCH Profil (partiel): {'✅' if profile_success1 else '❌'}")
    print(f"   👤 PATCH Profil (champs vides): {'✅' if profile_success2 else '❌'}")
    print(f"   🏢 PATCH Entreprise (partiel): {'✅' if entreprise_success1 else '❌'}")
    print(f"   🏢 PATCH Entreprise (champs vides): {'✅' if entreprise_success2 else '❌'}")
    
    if profile_success1 and profile_success2 and entreprise_success1 and entreprise_success2:
        print(f"\n🎉 CORRECTIONS RÉUSSIES!")
        print(f"   ✅ Les champs vides ne causent plus d'erreurs 400")
        print(f"   ✅ Les modales frontend sont corrigées")
        print(f"   ✅ Plus d'erreurs de validation")
    else:
        print(f"\n⚠️  Des problèmes persistent")
        print(f"   - Vérifier les validations backend")
        print(f"   - Vérifier les types de données")

if __name__ == "__main__":
    main()























































