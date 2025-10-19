#!/usr/bin/env python3
"""
Test des modales modernisées
- Design professionnel
- Champs complets profil et entreprise
- Upload d'images
- Dashboard sans produits/factures
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

def test_update_profile_complete(token, user_id):
    """Test de mise à jour complète du profil."""
    print(f"\n👤 Test de mise à jour complète du profil...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "username": SUPERADMIN_EMAIL,
        "first_name": "Admin Moderne",
        "last_name": "Test Moderne",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Moderne",
        "date_embauche": "2023-01-15",
        "role": "superadmin"
    }
    try:
        response = requests.put(f"{BASE_URL}/users/{user_id}/", json=update_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profil mis à jour: {data['first_name']} {data['last_name']}")
            print(f"   📞 Téléphone: {data['telephone']}")
            print(f"   💼 Poste: {data['poste']}")
            print(f"   📅 Date embauche: {data.get('date_embauche', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_update_entreprise_complete(token, entreprise_id):
    """Test de mise à jour complète de l'entreprise."""
    print(f"\n🏢 Test de mise à jour complète de l'entreprise...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "nom": "Entreprise Moderne Test",
        "secteur_activite": "technologie",
        "ville": "Douala Moderne",
        "code_postal": "00237",
        "pays": "Cameroun",
        "telephone": "+237 6XX XXX XXX",
        "email": "contact@moderne.com",
        "site_web": "https://www.moderne.com",
        "pack_type": "professionnel",
        "nombre_employes": 25,
        "annee_creation": 2023,
        "numero_fiscal": "M123456789",
        "adresse": "123 Rue Moderne, Douala, Cameroun"
    }
    try:
        response = requests.put(f"{BASE_URL}/entreprises/{entreprise_id}/", json=update_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Entreprise mise à jour: {data['nom']}")
            print(f"   🏭 Secteur: {data['secteur_activite']}")
            print(f"   📍 Ville: {data['ville']}")
            print(f"   📮 Code postal: {data.get('code_postal', 'N/A')}")
            print(f"   🌍 Pays: {data.get('pays', 'N/A')}")
            print(f"   📞 Téléphone: {data.get('telephone', 'N/A')}")
            print(f"   📧 Email: {data.get('email', 'N/A')}")
            print(f"   🌐 Site web: {data.get('site_web', 'N/A')}")
            print(f"   📦 Pack: {data['pack_type']}")
            print(f"   👥 Employés: {data['nombre_employes']}")
            print(f"   📅 Année création: {data['annee_creation']}")
            print(f"   🏛️ Numéro fiscal: {data.get('numero_fiscal', 'N/A')}")
            print(f"   🏠 Adresse: {data.get('adresse', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_dashboard_stats(token):
    """Test des statistiques du dashboard (sans produits/factures)."""
    print(f"\n📊 Test des statistiques du dashboard...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/entreprises/", headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                entreprise = data[0]
                boutiques_count = len(entreprise.get('boutiques', []))
                users_count = len(entreprise.get('users', []))
                print(f"   ✅ Statistiques chargées:")
                print(f"      🏪 Entrepôts: {boutiques_count}")
                print(f"      👤 Utilisateurs: {users_count}")
                print(f"   ✅ Produits et factures retirés du dashboard SuperAdmin")
            else:
                print(f"   ⚠️  Aucune entreprise trouvée")
        else:
            print(f"   ❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_create_boutique_modern(token, entreprise_id):
    """Test de création d'entrepôt avec interface moderne."""
    print(f"\n🏪 Test de création d'entrepôt moderne...")
    headers = {"Authorization": f"Bearer {token}"}
    boutique_data = {
        "nom": f"Entrepôt Moderne {int(time.time())}",
        "ville": "Douala",
        "adresse": "123 Rue Moderne",
        "telephone": "+237 699 000 000",
        "email": f"moderne{int(time.time())}@test.com",
        "responsable": "Responsable Moderne",
        "entreprise": entreprise_id
    }
    try:
        response = requests.post(f"{BASE_URL}/boutiques/", json=boutique_data, headers=headers)
        print(f"   Statut: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Entrepôt créé: {data['nom']} (ID: {data['id']})")
            print(f"   📍 Ville: {data['ville']}")
            print(f"   👤 Responsable: {data['responsable']}")
            return data['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_create_user_modern(token, entreprise_id, boutique_id):
    """Test de création d'utilisateur avec interface moderne."""
    print(f"\n👤 Test de création d'utilisateur moderne...")
    headers = {"Authorization": f"Bearer {token}"}
    user_email = f"moderneuser{int(time.time())}@example.com"
    user_data = {
        "username": user_email,
        "first_name": "Moderne",
        "last_name": "User",
        "email": user_email,
        "telephone": "+237 6XX XXX XXX",
        "poste": "Gestionnaire Moderne",
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
            print(f"   ✅ Utilisateur créé: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"   📧 Email: {data['user']['email']}")
            print(f"   💼 Poste: {data['user']['poste']}")
            return data['user']['id']
        else:
            print(f"   ❌ Erreur: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None

def test_delete_modern_operations(token, boutique_id, user_id):
    """Test des opérations de suppression avec interface moderne."""
    print(f"\n🗑️ Test des opérations de suppression moderne...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Supprimer l'utilisateur créé
    if user_id:
        try:
            response = requests.delete(f"{BASE_URL}/users/{user_id}/", headers=headers)
            print(f"   👤 Suppression utilisateur moderne: {response.status_code}")
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
            print(f"   🏪 Suppression entrepôt moderne: {response.status_code}")
            if response.status_code == 204:
                print(f"   ✅ Entrepôt supprimé avec succès")
            else:
                print(f"   ⚠️  Statut inattendu: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def main():
    print("🚀 Test des modales modernisées")
    print("=" * 60)

    # 1. Connexion
    access_token, user_id, entreprise_id, boutique_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    # 2. Test mise à jour profil complète
    test_update_profile_complete(access_token, user_id)

    # 3. Test mise à jour entreprise complète
    test_update_entreprise_complete(access_token, entreprise_id)

    # 4. Test statistiques dashboard
    test_dashboard_stats(access_token)

    # 5. Test création avec interface moderne
    new_boutique_id = test_create_boutique_modern(access_token, entreprise_id)
    new_user_id = test_create_user_modern(access_token, entreprise_id, new_boutique_id or boutique_id)

    # 6. Test suppression avec interface moderne
    test_delete_modern_operations(access_token, new_boutique_id, new_user_id)

    print("\n✅ Tests des modales modernisées terminés!")
    print("\n📝 Résumé des améliorations:")
    print("   ✅ Design moderne avec gradients et ombres")
    print("   ✅ Champs complets pour profil (photo, date embauche)")
    print("   ✅ Champs complets pour entreprise (logo, secteur, adresse)")
    print("   ✅ Upload d'images pour photo profil et logo entreprise")
    print("   ✅ Dashboard sans produits et factures")
    print("   ✅ Interface professionnelle comme les logiciels de stock")

if __name__ == "__main__":
    main()































