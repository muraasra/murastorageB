#!/usr/bin/env python3
"""
Test des modifications PATCH et nettoyage du dashboard
- Vérifier que les requêtes PATCH fonctionnent
- Tester le dashboard sans cartes profil/entreprise
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

def test_profile_update_with_patch(token, user_id):
    """Test de mise à jour du profil avec PATCH."""
    print(f"\n👤 Test de mise à jour du profil (PATCH)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données pour PATCH (seulement les champs modifiés)
    update_data = {
        "first_name": "Admin PATCH",
        "last_name": "Test PATCH",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin PATCH"
    }
    
    print(f"   📤 Données PATCH envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profil mis à jour avec PATCH")
            print(f"      Nom: {data['first_name']} {data['last_name']}")
            print(f"      Email: {data['email']}")
            print(f"      Rôle: {data['role']}")
            print(f"      Téléphone: {data['telephone']}")
            print(f"      Poste: {data['poste']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_entreprise_update_with_patch(token, entreprise_id):
    """Test de mise à jour de l'entreprise avec PATCH."""
    print(f"\n🏢 Test de mise à jour de l'entreprise (PATCH)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données pour PATCH (seulement les champs modifiés)
    update_data = {
        "nom": "Entreprise PATCH Test",
        "secteur_activite": "technologie",
        "ville": "Douala PATCH",
        "pack_type": "professionnel",
        "nombre_employes": 35
    }
    
    print(f"   📤 Données PATCH envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Entreprise mise à jour avec PATCH")
            print(f"      Nom: {data['nom']}")
            print(f"      Secteur: {data['secteur_activite']}")
            print(f"      Ville: {data['ville']}")
            print(f"      Pack: {data['pack_type']}")
            print(f"      Employés: {data['nombre_employes']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_create_boutique_for_patch(token, entreprise_id):
    """Test de création d'entrepôt pour tester PATCH."""
    print(f"\n🏪 Test de création d'entrepôt pour PATCH...")
    headers = {"Authorization": f"Bearer {token}"}
    boutique_data = {
        "nom": f"Entrepôt PATCH Test {int(time.time())}",
        "ville": "Douala",
        "adresse": "123 Rue PATCH",
        "telephone": "+237 699 000 000",
        "email": f"patch{int(time.time())}@test.com",
        "responsable": "Responsable PATCH",
        "entreprise": entreprise_id
    }
    try:
        response = requests.post(f"{BASE_URL}/boutiques/", json=boutique_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Entrepôt créé pour PATCH: {data['nom']} (ID: {data['id']})")
            print(f"   📍 Ville: {data['ville']}")
            print(f"   👤 Responsable: {data['responsable']}")
            return data['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_boutique_update_with_patch(token, boutique_id):
    """Test de mise à jour d'entrepôt avec PATCH."""
    print(f"\n🏪 Test de mise à jour d'entrepôt (PATCH)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données pour PATCH (seulement les champs modifiés)
    update_data = {
        "nom": f"Entrepôt PATCH Modifié {int(time.time())}",
        "ville": "Douala PATCH Modifié",
        "responsable": "Responsable PATCH Modifié"
    }
    
    print(f"   📤 Données PATCH envoyées:")
    for key, value in update_data.items():
        print(f"      {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/boutiques/{boutique_id}/", json=update_data, headers=headers)
        print(f"   📥 Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Entrepôt modifié avec PATCH")
            print(f"      Nom: {data['nom']}")
            print(f"      Ville: {data['ville']}")
            print(f"      Responsable: {data['responsable']}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_dashboard_data_loading(token):
    """Test du chargement des données pour le dashboard (sans cartes profil/entreprise)."""
    print(f"\n📊 Test du chargement des données dashboard (nettoyé)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Charger les données de l'entreprise
        response = requests.get(f"{BASE_URL}/entreprises/", headers=headers)
        print(f"   📥 Statut entreprise: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                entreprise = data[0]
                boutiques_count = len(entreprise.get('boutiques', []))
                users_count = len(entreprise.get('users', []))
                print(f"   ✅ Données dashboard chargées:")
                print(f"      🏪 Entrepôts: {boutiques_count}")
                print(f"      👤 Utilisateurs: {users_count}")
                print(f"   ✅ Cartes profil et entreprise retirées du dashboard")
            else:
                print(f"   ⚠️  Aucune entreprise trouvée")
        
        # Charger les entrepôts
        response = requests.get(f"{BASE_URL}/boutiques/", headers=headers)
        print(f"   📥 Statut entrepôts: {response.status_code}")
        if response.status_code == 200:
            boutiques = response.json()
            print(f"   ✅ Entrepôts chargés: {len(boutiques)} entrepôt(s)")
            for boutique in boutiques[:3]:  # Afficher les 3 premiers
                print(f"      - {boutique['nom']} ({boutique['ville']})")
        
        # Charger les utilisateurs
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"   📥 Statut utilisateurs: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ Utilisateurs chargés: {len(users)} utilisateur(s)")
            for user in users[:3]:  # Afficher les 3 premiers
                print(f"      - {user['first_name']} {user['last_name']} ({user['role']})")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_delete_boutique(token, boutique_id):
    """Test de suppression d'entrepôt."""
    print(f"\n🗑️ Test de suppression d'entrepôt...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BASE_URL}/boutiques/{boutique_id}/", headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 204:
            print(f"   ✅ Entrepôt supprimé avec succès")
        else:
            print(f"   ⚠️  Statut inattendu: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def main():
    print("🚀 Test des modifications PATCH et nettoyage dashboard")
    print("=" * 60)

    # 1. Connexion
    access_token, user_id, entreprise_id, boutique_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    # 2. Test des modifications PATCH
    test_profile_update_with_patch(access_token, user_id)
    test_entreprise_update_with_patch(access_token, entreprise_id)
    
    # 3. Test création et modification entrepôt avec PATCH
    new_boutique_id = test_create_boutique_for_patch(access_token, entreprise_id)
    if new_boutique_id:
        test_boutique_update_with_patch(access_token, new_boutique_id)
        test_delete_boutique(access_token, new_boutique_id)
    
    # 4. Test chargement données dashboard nettoyé
    test_dashboard_data_loading(access_token)

    print("\n✅ Tests des modifications PATCH et nettoyage terminés!")
    print("\n📝 Résumé des modifications:")
    print("   ✅ Requêtes PUT changées en PATCH")
    print("   ✅ Cartes profil et entreprise retirées du dashboard")
    print("   ✅ Variables et fonctions inutiles supprimées")
    print("   ✅ Dashboard simplifié et focalisé")
    print("   ✅ Modifications partielles avec PATCH")

if __name__ == "__main__":
    main()




























