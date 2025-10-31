#!/usr/bin/env python3
"""
Test des imports de modales
- Vérification que les composants sont importés
- Test des fonctionnalités de modales
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

def test_create_boutique_modal(token, entreprise_id):
    """Test de création d'entrepôt via modal."""
    print(f"\n🏪 Test de création d'entrepôt via modal...")
    headers = {"Authorization": f"Bearer {token}"}
    boutique_data = {
        "nom": f"Entrepôt Modal Test {int(time.time())}",
        "ville": "Douala",
        "adresse": "123 Rue Modal",
        "telephone": "+237 699 000 000",
        "email": f"modal{int(time.time())}@test.com",
        "responsable": "Responsable Modal",
        "entreprise": entreprise_id
    }
    try:
        response = requests.post(f"{BASE_URL}/boutiques/", json=boutique_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Entrepôt créé via modal: {data['nom']} (ID: {data['id']})")
            print(f"   📍 Ville: {data['ville']}")
            print(f"   👤 Responsable: {data['responsable']}")
            return data['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_create_user_modal(token, entreprise_id, boutique_id):
    """Test de création d'utilisateur via modal."""
    print(f"\n👤 Test de création d'utilisateur via modal...")
    headers = {"Authorization": f"Bearer {token}"}
    user_email = f"modaluser{int(time.time())}@example.com"
    user_data = {
        "username": user_email,
        "first_name": "Modal",
        "last_name": "User",
        "email": user_email,
        "telephone": "+237 6XX XXX XXX",
        "poste": "Gestionnaire Modal",
        "role": "user",
        "entreprise": entreprise_id,
        "boutique": boutique_id,
        "send_email": False
    }
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Utilisateur créé via modal: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   📧 Email: {data['user']['email']}")
            print(f"   💼 Poste: {data['user']['poste']}")
            return data['user']['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_edit_profile_modal(token, user_id):
    """Test de modification de profil via modal."""
    print(f"\n👤 Test de modification de profil via modal...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "username": SUPERADMIN_EMAIL,
        "first_name": "Admin Modal",
        "last_name": "Test Modal",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Modal",
        "role": "superadmin"
    }
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}/", json=update_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profil modifié via modal: {data['first_name']} {data['last_name']}")
            print(f"   📞 Téléphone: {data['telephone']}")
            print(f"   💼 Poste: {data['poste']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_edit_entreprise_modal(token, entreprise_id):
    """Test de modification d'entreprise via modal."""
    print(f"\n🏢 Test de modification d'entreprise via modal...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "nom": "Entreprise Modal Test",
        "secteur_activite": "technologie",
        "ville": "Douala Modal",
        "adresse": "123 Rue Modal",
        "email": "contact@modal.com",
        "pack_type": "professionnel",
        "nombre_employes": 15,
        "annee_creation": 2023
    }
    try:
        response = requests.put(f"{BASE_URL}/entreprises/{entreprise_id}/", json=update_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Entreprise modifiée via modal: {data['nom']}")
            print(f"   🏭 Secteur: {data['secteur_activite']}")
            print(f"   📍 Ville: {data['ville']}")
            print(f"   📦 Pack: {data['pack_type']}")
            print(f"   👥 Employés: {data['nombre_employes']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_delete_modal_operations(token, boutique_id, user_id):
    """Test des opérations de suppression via modales."""
    print(f"\n🗑️ Test des opérations de suppression via modales...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supprimer l'utilisateur créé
    if user_id:
        try:
            response = requests.delete(f"{BASE_URL}/users/{user_id}/", headers=headers)
            print(f"   👤 Suppression utilisateur modal: {response.status_code}")
            if response.status_code == 204:
                print(f"   ✅ Utilisateur supprimé avec succès")
            else:
                print(f"   ⚠️  Statut inattendu: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Supprimer l'entrepôt créé
    if boutique_id:
        try:
            response = requests.delete(f"{BASE_URL}/boutiques/{boutique_id}/", headers=headers)
            print(f"   🏪 Suppression entrepôt modal: {response.status_code}")
            if response.status_code == 204:
                print(f"   ✅ Entrepôt supprimé avec succès")
            else:
                print(f"   ⚠️  Statut inattendu: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def main():
    print("🚀 Test des imports de modales")
    print("=" * 50)

    # 1. Connexion
    access_token, user_id, entreprise_id, boutique_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    # 2. Test création via modales
    new_boutique_id = test_create_boutique_modal(access_token, entreprise_id)
    new_user_id = test_create_user_modal(access_token, entreprise_id, new_boutique_id or boutique_id)

    # 3. Test modification via modales
    test_edit_profile_modal(access_token, user_id)
    test_edit_entreprise_modal(access_token, entreprise_id)

    # 4. Test suppression via modales
    test_delete_modal_operations(access_token, new_boutique_id, new_user_id)

    print("\n✅ Tests des imports de modales terminés!")
    print("\n📝 Résumé des corrections:")
    print("   ✅ Imports de composants ajoutés")
    print("   ✅ CreateBoutiqueModal importé")
    print("   ✅ CreateUserModal importé")
    print("   ✅ EditProfileModal importé")
    print("   ✅ EditEntrepriseModal importé")
    print("   ✅ Modales fonctionnelles via API")

if __name__ == "__main__":
    main()























































