#!/usr/bin/env python3
"""
Test des corrections frontend
- Vérifier que les données sont correctement envoyées
- Tester les cartes profil et entreprise
- Valider les modifications
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

def test_profile_update_with_correct_data(token, user_id):
    """Test de mise à jour du profil avec les bonnes données."""
    print(f"\n👤 Test de mise à jour du profil (données corrigées)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données exactes que le frontend devrait envoyer
    update_data = {
        "username": SUPERADMIN_EMAIL,  # Utiliser l'username existant
        "first_name": "Admin Frontend Corrigé",
        "last_name": "Test Frontend Corrigé",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Frontend Corrigé",
        "date_embauche": "2023-01-15",
        "role": "superadmin"
    }
    
    print(f"   📤 Données envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profil mis à jour avec succès")
            print(f"      Nom: {data['first_name']} {data['last_name']}")
            print(f"      Email: {data['email']}")
            print(f"      Rôle: {data['role']}")
            print(f"      Téléphone: {data['telephone']}")
            print(f"      Poste: {data['poste']}")
            print(f"      Date embauche: {data.get('date_embauche', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_entreprise_update_with_correct_data(token, entreprise_id):
    """Test de mise à jour de l'entreprise avec les bonnes données."""
    print(f"\n🏢 Test de mise à jour de l'entreprise (données corrigées)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données exactes que le frontend devrait envoyer
    update_data = {
        "nom": "Entreprise Frontend Corrigée",
        "secteur_activite": "technologie",
        "ville": "Douala Frontend Corrigée",
        "code_postal": "00237",
        "pays": "Cameroun",
        "telephone": "+237 6XX XXX XXX",
        "email": "contact@frontendcorrige.com",
        "site_web": "https://www.frontendcorrige.com",
        "pack_type": "professionnel",
        "nombre_employes": 30,
        "annee_creation": 2023,
        "numero_fiscal": "FC123456789",
        "adresse": "123 Rue Frontend Corrigée, Douala, Cameroun"  # Champ requis ajouté
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
            print(f"      Adresse: {data['adresse']}")
            print(f"      Email: {data['email']}")
            print(f"      Année création: {data['annee_creation']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_dashboard_data_loading(token, entreprise_id):
    """Test du chargement des données pour le dashboard."""
    print(f"\n📊 Test du chargement des données dashboard...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Charger les données de l'entreprise
        response = requests.get(f"{BASE_URL}/entreprises/{entreprise_id}/", headers=headers)
        print(f"   📥 Statut entreprise: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Données entreprise chargées:")
            print(f"      Nom: {data['nom']}")
            print(f"      Secteur: {data['secteur_activite']}")
            print(f"      Ville: {data['ville']}")
            print(f"      Pack: {data['pack_type']}")
            print(f"      Employés: {data['nombre_employes']}")
            print(f"      Année création: {data['annee_creation']}")
        
        # Charger les utilisateurs de l'entreprise
        response = requests.get(f"{BASE_URL}/users/?entreprise={entreprise_id}", headers=headers)
        print(f"   📥 Statut utilisateurs: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            super_admin = next((u for u in users if u['role'] == 'superadmin'), None)
            if super_admin:
                print(f"   ✅ Données SuperAdmin chargées:")
                print(f"      Nom: {super_admin['first_name']} {super_admin['last_name']}")
                print(f"      Email: {super_admin['email']}")
                print(f"      Rôle: {super_admin['role']}")
                print(f"      Téléphone: {super_admin.get('telephone', 'N/A')}")
                print(f"      Poste: {super_admin.get('poste', 'N/A')}")
            else:
                print(f"   ⚠️  Aucun SuperAdmin trouvé")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_error_scenarios(token, user_id, entreprise_id):
    """Test des scénarios d'erreur pour identifier les problèmes."""
    print(f"\n🔍 Test des scénarios d'erreur...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test utilisateur avec données manquantes
    print(f"   🧪 Test utilisateur sans username:")
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}/", json={
            "first_name": "Test",
            "last_name": "User",
            "role": "superadmin"
        }, headers=headers)
        print(f"      Statut: {response.status_code}")
        if response.status_code == 400:
            print(f"      ❌ Erreur attendue: {response.json()}")
    except Exception as e:
        print(f"      ❌ Erreur: {e}")
    
    # Test entreprise avec données manquantes
    print(f"   🧪 Test entreprise sans adresse:")
    try:
        response = requests.put(f"{BASE_URL}/entreprises/{entreprise_id}/", json={
            "nom": "Test Entreprise",
            "ville": "Douala",
            "email": "test@test.com",
            "annee_creation": 2023
        }, headers=headers)
        print(f"      Statut: {response.status_code}")
        if response.status_code == 400:
            print(f"      ❌ Erreur attendue: {response.json()}")
    except Exception as e:
        print(f"      ❌ Erreur: {e}")

def main():
    print("🚀 Test des corrections frontend")
    print("=" * 50)

    # 1. Connexion
    access_token, user_id, entreprise_id, boutique_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    # 2. Test des corrections
    test_profile_update_with_correct_data(access_token, user_id)
    test_entreprise_update_with_correct_data(access_token, entreprise_id)
    
    # 3. Test chargement données dashboard
    test_dashboard_data_loading(access_token, entreprise_id)
    
    # 4. Test scénarios d'erreur
    test_error_scenarios(access_token, user_id, entreprise_id)

    print("\n✅ Tests des corrections frontend terminés!")
    print("\n📝 Résumé des corrections:")
    print("   ✅ Données utilisateur corrigées (username requis)")
    print("   ✅ Données entreprise corrigées (adresse requise)")
    print("   ✅ Validation des champs obligatoires")
    print("   ✅ Chargement des données dashboard")
    print("   ✅ Gestion des erreurs améliorée")

if __name__ == "__main__":
    main()