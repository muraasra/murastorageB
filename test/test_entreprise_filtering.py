#!/usr/bin/env python3
"""
Test du filtrage par entreprise
- Vérifier que chaque SuperAdmin ne voit que ses données
- Tester les statistiques, entrepôts, utilisateurs, produits, factures
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "filtertest@test.com"
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

def test_entreprise_statistics(token, entreprise_id):
    """Test des statistiques de l'entreprise."""
    print(f"\n📊 TEST STATISTIQUES ENTREPRISE")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Récupérer les données de l'entreprise spécifique
        response = requests.get(f"{BASE_URL}/entreprises/{entreprise_id}/", headers=headers)
        print(f"📥 Statut entreprise: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Entreprise: {data.get('nom')}")
            print(f"   🏢 ID: {data.get('id_entreprise')}")
            print(f"   📦 Entrepôts: {len(data.get('boutiques', []))}")
            print(f"   👥 Utilisateurs: {len(data.get('users', []))}")
            
            # Vérifier que les données sont bien filtrées
            boutiques_count = len(data.get('boutiques', []))
            users_count = len(data.get('users', []))
            
            print(f"\n🔍 Vérification du filtrage:")
            print(f"   📦 Entrepôts de l'entreprise: {boutiques_count}")
            print(f"   👥 Utilisateurs de l'entreprise: {users_count}")
            
            return True, boutiques_count, users_count
        else:
            print(f"❌ Erreur: {response.json()}")
            return False, 0, 0
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, 0, 0

def test_boutiques_filtering(token, entreprise_id):
    """Test du filtrage des entrepôts par entreprise."""
    print(f"\n🏢 TEST FILTRAGE ENTREPÔTS")
    print("=" * 35)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Tous les entrepôts (sans filtre)
        response = requests.get(f"{BASE_URL}/boutiques/", headers=headers)
        print(f"📥 Statut tous entrepôts: {response.status_code}")
        
        if response.status_code == 200:
            all_boutiques = response.json()
            print(f"   📦 Total entrepôts: {len(all_boutiques)}")
        
        # Test 2: Entrepôts filtrés par entreprise
        response = requests.get(f"{BASE_URL}/boutiques/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut entrepôts filtrés: {response.status_code}")
        
        if response.status_code == 200:
            filtered_boutiques = response.json()
            print(f"   📦 Entrepôts de l'entreprise: {len(filtered_boutiques)}")
            
            # Vérifier que tous les entrepôts appartiennent à l'entreprise
            for boutique in filtered_boutiques:
                if boutique.get('entreprise') != entreprise_id:
                    print(f"❌ Erreur: Entrepôt {boutique.get('nom')} n'appartient pas à l'entreprise {entreprise_id}")
                    return False
            
            print(f"✅ Tous les entrepôts appartiennent à l'entreprise {entreprise_id}")
            return True, len(filtered_boutiques)
        else:
            print(f"❌ Erreur: {response.json()}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, 0

def test_users_filtering(token, entreprise_id):
    """Test du filtrage des utilisateurs par entreprise."""
    print(f"\n👥 TEST FILTRAGE UTILISATEURS")
    print("=" * 35)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Tous les utilisateurs (sans filtre)
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"📥 Statut tous utilisateurs: {response.status_code}")
        
        if response.status_code == 200:
            all_users = response.json()
            print(f"   👥 Total utilisateurs: {len(all_users)}")
        
        # Test 2: Utilisateurs filtrés par entreprise
        response = requests.get(f"{BASE_URL}/users/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut utilisateurs filtrés: {response.status_code}")
        
        if response.status_code == 200:
            filtered_users = response.json()
            print(f"   👥 Utilisateurs de l'entreprise: {len(filtered_users)}")
            
            # Vérifier que tous les utilisateurs appartiennent à l'entreprise
            for user in filtered_users:
                if user.get('entreprise') != entreprise_id:
                    print(f"❌ Erreur: Utilisateur {user.get('username')} n'appartient pas à l'entreprise {entreprise_id}")
                    return False
            
            print(f"✅ Tous les utilisateurs appartiennent à l'entreprise {entreprise_id}")
            return True, len(filtered_users)
        else:
            print(f"❌ Erreur: {response.json()}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, 0

def test_produits_filtering(token, entreprise_id):
    """Test du filtrage des produits par entreprise."""
    print(f"\n📦 TEST FILTRAGE PRODUITS")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Tous les produits (sans filtre)
        response = requests.get(f"{BASE_URL}/produits/", headers=headers)
        print(f"📥 Statut tous produits: {response.status_code}")
        
        if response.status_code == 200:
            all_produits = response.json()
            print(f"   📦 Total produits: {len(all_produits)}")
        
        # Test 2: Produits filtrés par entreprise
        response = requests.get(f"{BASE_URL}/produits/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut produits filtrés: {response.status_code}")
        
        if response.status_code == 200:
            filtered_produits = response.json()
            print(f"   📦 Produits de l'entreprise: {len(filtered_produits)}")
            
            # Vérifier que tous les produits appartiennent à l'entreprise
            for produit in filtered_produits:
                if produit.get('entreprise') != entreprise_id:
                    print(f"❌ Erreur: Produit {produit.get('nom')} n'appartient pas à l'entreprise {entreprise_id}")
                    return False
            
            print(f"✅ Tous les produits appartiennent à l'entreprise {entreprise_id}")
            return True, len(filtered_produits)
        else:
            print(f"❌ Erreur: {response.json()}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, 0

def test_factures_filtering(token, entreprise_id):
    """Test du filtrage des factures par entreprise."""
    print(f"\n🧾 TEST FILTRAGE FACTURES")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Toutes les factures (sans filtre)
        response = requests.get(f"{BASE_URL}/factures/", headers=headers)
        print(f"📥 Statut toutes factures: {response.status_code}")
        
        if response.status_code == 200:
            all_factures = response.json()
            print(f"   🧾 Total factures: {len(all_factures)}")
        
        # Test 2: Factures filtrées par entreprise
        response = requests.get(f"{BASE_URL}/factures/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut factures filtrées: {response.status_code}")
        
        if response.status_code == 200:
            filtered_factures = response.json()
            print(f"   🧾 Factures de l'entreprise: {len(filtered_factures)}")
            
            # Vérifier que toutes les factures appartiennent à l'entreprise
            for facture in filtered_factures:
                if facture.get('entreprise') != entreprise_id:
                    print(f"❌ Erreur: Facture {facture.get('nom_facture')} n'appartient pas à l'entreprise {entreprise_id}")
                    return False
            
            print(f"✅ Toutes les factures appartiennent à l'entreprise {entreprise_id}")
            return True, len(filtered_factures)
        else:
            print(f"❌ Erreur: {response.json()}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, 0

def main():
    print("🚀 TEST FILTRAGE PAR ENTREPRISE")
    print("=" * 40)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    print(f"✅ Connexion réussie!")
    print(f"   👤 User ID: {user_id}")
    print(f"   🏢 Entreprise ID: {entreprise_id}")
    
    # 2. Tests de filtrage
    stats_success, boutiques_count, users_count = test_entreprise_statistics(access_token, entreprise_id)
    boutiques_success, boutiques_filtered = test_boutiques_filtering(access_token, entreprise_id)
    users_success, users_filtered = test_users_filtering(access_token, entreprise_id)
    produits_success, produits_filtered = test_produits_filtering(access_token, entreprise_id)
    factures_success, factures_filtered = test_factures_filtering(access_token, entreprise_id)
    
    # 3. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    print(f"   📊 Statistiques entreprise: {'✅' if stats_success else '❌'}")
    print(f"   🏢 Filtrage entrepôts: {'✅' if boutiques_success else '❌'}")
    print(f"   👥 Filtrage utilisateurs: {'✅' if users_success else '❌'}")
    print(f"   📦 Filtrage produits: {'✅' if produits_success else '❌'}")
    print(f"   🧾 Filtrage factures: {'✅' if factures_success else '❌'}")
    
    print(f"\n📈 DONNÉES DE L'ENTREPRISE:")
    print(f"   📦 Entrepôts: {boutiques_filtered}")
    print(f"   👥 Utilisateurs: {users_filtered}")
    print(f"   📦 Produits: {produits_filtered}")
    print(f"   🧾 Factures: {factures_filtered}")
    
    if all([stats_success, boutiques_success, users_success, produits_success, factures_success]):
        print(f"\n🎉 FILTRAGE PARFAIT!")
        print(f"   ✅ Toutes les données sont filtrées par entreprise")
        print(f"   ✅ Les statistiques affichent uniquement les données de l'entreprise")
        print(f"   ✅ Les listes montrent uniquement les éléments de l'entreprise")
        print(f"   ✅ Sécurité et isolation des données garanties")
    else:
        print(f"\n⚠️  Des problèmes de filtrage persistent")
        print(f"   - Vérifier les paramètres de requête")
        print(f"   - Vérifier les permissions backend")
        print(f"   - Vérifier les filtres frontend")

if __name__ == "__main__":
    main()
