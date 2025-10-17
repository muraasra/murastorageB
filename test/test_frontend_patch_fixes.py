#!/usr/bin/env python3
"""
Test des corrections des requêtes PATCH frontend
- Simuler les données envoyées par le frontend
- Vérifier que les requêtes PATCH fonctionnent
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

def test_profile_patch_frontend_simulation(token, user_id):
    """Test PATCH profil avec les données du frontend corrigé."""
    print(f"\n👤 TEST PATCH PROFIL (Simulation Frontend Corrigé)")
    print("=" * 55)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données comme envoyées par le frontend corrigé
    patch_data = {
        "first_name": "Admin Frontend",
        "last_name": "Test Frontend",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Frontend",
        "date_embauche": "2023-01-15",
        "is_active_employee": True
    }
    
    print(f"📤 Données PATCH (Frontend corrigé):")
    for key, value in patch_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   👨 Nom: {data.get('first_name')} {data.get('last_name')}")
            print(f"   📞 Téléphone: {data.get('telephone')}")
            print(f"   💼 Poste: {data.get('poste')}")
            print(f"   📅 Date embauche: {data.get('date_embauche')}")
            print(f"   ✅ Statut: {data.get('is_active_employee')}")
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

def test_entreprise_patch_frontend_simulation(token, entreprise_id):
    """Test PATCH entreprise avec les données du frontend corrigé."""
    print(f"\n🏢 TEST PATCH ENTREPRISE (Simulation Frontend Corrigé)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données comme envoyées par le frontend corrigé
    patch_data = {
        "nom": "Entreprise Frontend Test",
        "description": "Description mise à jour par frontend",
        "secteur_activite": "technologie",
        "ville": "Douala Frontend",
        "code_postal": "00237",
        "pays": "Cameroun",
        "telephone": "+237 6XX XXX XXX",
        "email": "contact@frontend.com",
        "site_web": "https://www.frontend.com",
        "pack_type": "professionnel",
        "nombre_employes": 30,
        "annee_creation": 2023,
        "numero_fiscal": "F123456789",
        "pack_prix": 150.0,
        "pack_duree": "mensuel",
        "is_active": True,
        "adresse": "123 Rue Frontend, Douala, Cameroun"
    }
    
    print(f"📤 Données PATCH (Frontend corrigé):")
    for key, value in patch_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   🏢 Nom: {data.get('nom')}")
            print(f"   📝 Description: {data.get('description')}")
            print(f"   🏭 Secteur: {data.get('secteur_activite')}")
            print(f"   🏙️ Ville: {data.get('ville')}")
            print(f"   📦 Pack: {data.get('pack_type')}")
            print(f"   💰 Prix: {data.get('pack_prix')}")
            print(f"   ⏱️ Durée: {data.get('pack_duree')}")
            print(f"   ✅ Actif: {data.get('is_active')}")
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

def test_profile_patch_with_password(token, user_id):
    """Test PATCH profil avec mot de passe."""
    print(f"\n🔒 TEST PATCH PROFIL AVEC MOT DE PASSE")
    print("=" * 45)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données avec mot de passe
    patch_data = {
        "first_name": "Admin Password",
        "last_name": "Test Password",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Password",
        "date_embauche": "2023-01-15",
        "is_active_employee": True,
        "password": "newpassword123"
    }
    
    print(f"📤 Données PATCH avec mot de passe:")
    for key, value in patch_data.items():
        if key == "password":
            print(f"   {key}: [MASQUÉ]")
        else:
            print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès avec mot de passe!")
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

def test_entreprise_validation(token, entreprise_id):
    """Test de validation des champs entreprise."""
    print(f"\n🔍 TEST VALIDATION ENTREPRISE")
    print("=" * 35)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec des données invalides
    invalid_data = {
        "annee_creation": 2030,  # Année future
        "nombre_employes": -5   # Nombre négatif
    }
    
    print(f"📤 Données invalides:")
    print(f"   annee_creation: 2030 (future)")
    print(f"   nombre_employes: -5 (négatif)")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=invalid_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            print(f"✅ Validation fonctionne (erreur 400 attendue)")
            print(f"   Erreurs: {error_data}")
            return True
        else:
            print(f"⚠️  Validation ne fonctionne pas (statut {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 TEST DES CORRECTIONS PATCH FRONTEND")
    print("=" * 45)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Tests PATCH avec données frontend corrigées
    profile_success = test_profile_patch_frontend_simulation(access_token, user_id)
    entreprise_success = test_entreprise_patch_frontend_simulation(access_token, entreprise_id)
    
    # 3. Test avec mot de passe
    password_success = test_profile_patch_with_password(access_token, user_id)
    
    # 4. Test de validation
    validation_success = test_entreprise_validation(access_token, entreprise_id)
    
    # 5. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    print(f"   👤 PATCH Profil: {'✅' if profile_success else '❌'}")
    print(f"   🏢 PATCH Entreprise: {'✅' if entreprise_success else '❌'}")
    print(f"   🔒 PATCH avec mot de passe: {'✅' if password_success else '❌'}")
    print(f"   🔍 Validation: {'✅' if validation_success else '❌'}")
    
    if profile_success and entreprise_success:
        print(f"\n🎉 CORRECTIONS RÉUSSIES!")
        print(f"   ✅ Les requêtes PATCH fonctionnent")
        print(f"   ✅ Les modales frontend sont corrigées")
        print(f"   ✅ Plus d'erreurs 400")
    else:
        print(f"\n⚠️  Des problèmes persistent")
        print(f"   - Vérifier les serializers backend")
        print(f"   - Vérifier les permissions")
        print(f"   - Vérifier les validations")

if __name__ == "__main__":
    main()

























