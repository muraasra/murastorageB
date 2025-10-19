#!/usr/bin/env python3
"""
Debug des erreurs 400 sur les requêtes PATCH
- Tester les requêtes PATCH pour users et entreprises
- Vérifier les données envoyées
- Identifier les problèmes de validation
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

def test_user_patch(token, user_id):
    """Test de la requête PATCH pour l'utilisateur."""
    print(f"\n👤 TEST PATCH UTILISATEUR (ID: {user_id})")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données de test pour PATCH
    patch_data = {
        "first_name": "Admin Test",
        "last_name": "PATCH Test",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Super Admin Test",
        "date_embauche": "2023-01-15",
        "is_active_employee": True
    }
    
    print(f"📤 Données PATCH envoyées:")
    for key, value in patch_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   👨 Nom: {data.get('first_name')} {data.get('last_name')}")
            print(f"   📞 Téléphone: {data.get('telephone')}")
            print(f"   💼 Poste: {data.get('poste')}")
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

def test_entreprise_patch(token, entreprise_id):
    """Test de la requête PATCH pour l'entreprise."""
    print(f"\n🏢 TEST PATCH ENTREPRISE (ID: {entreprise_id})")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données de test pour PATCH
    patch_data = {
        "nom": "Entreprise Test PATCH",
        "secteur_activite": "technologie",
        "ville": "Douala Test",
        "code_postal": "00237",
        "pays": "Cameroun",
        "telephone": "+237 6XX XXX XXX",
        "email": "contact@test.com",
        "site_web": "https://www.test.com",
        "pack_type": "professionnel",
        "nombre_employes": 25,
        "annee_creation": 2023,
        "numero_fiscal": "T123456789",
        "adresse": "123 Rue Test, Douala, Cameroun"
    }
    
    print(f"📤 Données PATCH envoyées:")
    for key, value in patch_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=patch_data, headers=headers)
        print(f"\n📥 Statut: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"   🏢 Nom: {data.get('nom')}")
            print(f"   🏭 Secteur: {data.get('secteur_activite')}")
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

def test_user_get(token, user_id):
    """Test de la requête GET pour l'utilisateur."""
    print(f"\n👤 TEST GET UTILISATEUR (ID: {user_id})")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données utilisateur récupérées:")
            print(f"   🆔 ID: {data.get('id')}")
            print(f"   👤 Username: {data.get('username')}")
            print(f"   👨 Prénom: {data.get('first_name')}")
            print(f"   👨 Nom: {data.get('last_name')}")
            print(f"   📧 Email: {data.get('email')}")
            print(f"   🎭 Rôle: {data.get('role')}")
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_entreprise_get(token, entreprise_id):
    """Test de la requête GET pour l'entreprise."""
    print(f"\n🏢 TEST GET ENTREPRISE (ID: {entreprise_id})")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/entreprises/{entreprise_id}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données entreprise récupérées:")
            print(f"   🆔 ID: {data.get('id')}")
            print(f"   🏢 Nom: {data.get('nom')}")
            print(f"   🏭 Secteur: {data.get('secteur_activite')}")
            print(f"   🏙️ Ville: {data.get('ville')}")
            return data
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_minimal_user_patch(token, user_id):
    """Test PATCH minimal pour l'utilisateur."""
    print(f"\n👤 TEST PATCH MINIMAL UTILISATEUR")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données minimales
    patch_data = {
        "first_name": "Admin Minimal"
    }
    
    print(f"📤 Données minimales:")
    print(f"   first_name: {patch_data['first_name']}")
    
    try:
        response = requests.patch(f"{BASE_URL}/users/{user_id}/", json=patch_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ PATCH minimal réussi!")
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

def test_minimal_entreprise_patch(token, entreprise_id):
    """Test PATCH minimal pour l'entreprise."""
    print(f"\n🏢 TEST PATCH MINIMAL ENTREPRISE")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données minimales
    patch_data = {
        "nom": "Entreprise Minimal"
    }
    
    print(f"📤 Données minimales:")
    print(f"   nom: {patch_data['nom']}")
    
    try:
        response = requests.patch(f"{BASE_URL}/entreprises/{entreprise_id}/", json=patch_data, headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ PATCH minimal réussi!")
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
    print("🚀 DEBUG DES ERREURS 400")
    print("=" * 30)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Tests GET pour vérifier les données existantes
    user_data = test_user_get(access_token, user_id)
    entreprise_data = test_entreprise_get(access_token, entreprise_id)
    
    # 3. Tests PATCH complets
    user_patch_success = test_user_patch(access_token, user_id)
    entreprise_patch_success = test_entreprise_patch(access_token, entreprise_id)
    
    # 4. Tests PATCH minimaux si les complets échouent
    if not user_patch_success:
        print(f"\n🔄 Test PATCH minimal utilisateur...")
        test_minimal_user_patch(access_token, user_id)
    
    if not entreprise_patch_success:
        print(f"\n🔄 Test PATCH minimal entreprise...")
        test_minimal_entreprise_patch(access_token, entreprise_id)
    
    # 5. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    print(f"   👤 PATCH Utilisateur: {'✅' if user_patch_success else '❌'}")
    print(f"   🏢 PATCH Entreprise: {'✅' if entreprise_patch_success else '❌'}")
    
    if not user_patch_success or not entreprise_patch_success:
        print(f"\n🔍 DIAGNOSTIC:")
        print(f"   - Vérifier les serializers Django")
        print(f"   - Vérifier les permissions")
        print(f"   - Vérifier les champs requis")
        print(f"   - Vérifier les validations")

if __name__ == "__main__":
    main()































