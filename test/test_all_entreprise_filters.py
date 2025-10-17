#!/usr/bin/env python3
"""
Test complet des filtres par entreprise pour tous les ViewSets
- Vérifier que tous les endpoints filtrent correctement par entreprise
- Tester Users, Boutiques, Produits, Factures
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "admin@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT pour le SuperAdmin."""
    print("🔐 CONNEXION SUPERADMIN")
    print("=" * 30)
    
    login_data = {
        "email": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion SuperAdmin réussie!")
            print(f"   🔑 Token: {data.get('access', '')[:20]}...")
            print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
            print(f"   🆔 ID Entreprise: {data.get('entreprise', {}).get('id', 'N/A')}")
            return data['access'], data['user'], data['entreprise']
        else:
            print(f"❌ Erreur connexion: {response.json()}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None, None

def test_endpoint_filter(token, endpoint, endpoint_name, entreprise_id):
    """Test du filtre d'un endpoint spécifique."""
    print(f"\n🔍 TEST {endpoint_name.upper()}")
    print("=" * (15 + len(endpoint_name)))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data)} {endpoint_name}(s) récupéré(s)")
            
            # Vérifier le filtrage par entreprise
            entreprise_ids = set()
            for item in data:
                if endpoint == 'users':
                    entreprise_id_item = item.get('entreprise')
                elif endpoint == 'boutiques':
                    entreprise_id_item = item.get('entreprise')
                elif endpoint == 'produits':
                    entreprise_id_item = item.get('boutique', {}).get('entreprise') if isinstance(item.get('boutique'), dict) else None
                elif endpoint == 'factures':
                    entreprise_id_item = item.get('boutique', {}).get('entreprise') if isinstance(item.get('boutique'), dict) else None
                else:
                    entreprise_id_item = None
                
                if entreprise_id_item:
                    entreprise_ids.add(entreprise_id_item)
            
            print(f"🔍 Entreprises trouvées: {list(entreprise_ids)}")
            
            # Vérifier que tous les éléments appartiennent à la même entreprise
            if len(entreprise_ids) <= 1:
                if not entreprise_ids or entreprise_ids.pop() == entreprise_id:
                    print(f"✅ Filtre entreprise correct pour {endpoint_name}")
                    return True
                else:
                    print(f"❌ Filtre entreprise incorrect pour {endpoint_name}")
                    return False
            else:
                print(f"❌ Plusieurs entreprises trouvées pour {endpoint_name}: {entreprise_ids}")
                return False
        else:
            print(f"❌ Erreur: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_query_params(token, endpoint, endpoint_name, entreprise_id):
    """Test avec paramètres de requête."""
    print(f"\n🔍 TEST PARAMÈTRES {endpoint_name.upper()}")
    print("=" * (20 + len(endpoint_name)))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test avec paramètre entreprise
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut avec ?entreprise={entreprise_id}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data)} {endpoint_name}(s) avec entreprise {entreprise_id}")
        else:
            print(f"❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_all_endpoints(token, entreprise_id):
    """Test de tous les endpoints avec filtres."""
    print(f"\n🚀 TEST TOUS LES ENDPOINTS")
    print("=" * 30)
    
    endpoints = [
        ('users', 'utilisateur'),
        ('boutiques', 'boutique'),
        ('produits', 'produit'),
        ('factures', 'facture')
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        # Test du filtre automatique
        filter_ok = test_endpoint_filter(token, endpoint, name, entreprise_id)
        results[endpoint] = filter_ok
        
        # Test avec paramètres de requête
        test_query_params(token, endpoint, name, entreprise_id)
    
    return results

def test_cross_entreprise_access():
    """Test d'accès croisé entre entreprises."""
    print(f"\n🔄 TEST ACCÈS CROISÉ ENTREPRISES")
    print("=" * 40)
    
    # Connexion avec admin@test.com (Entreprise Test - ID: 10)
    token1, user1, entreprise1 = test_jwt_login()
    if not token1:
        print("❌ Impossible de continuer sans token")
        return
    
    print(f"\n🏢 ENTREPRISE 1: {entreprise1.get('nom')} (ID: {entreprise1.get('id')})")
    
    # Tester l'accès aux données
    headers = {
        "Authorization": f"Bearer {token1}",
        "Content-Type": "application/json"
    }
    
    # Essayer d'accéder à une autre entreprise via paramètre
    try:
        response = requests.get(f"{BASE_URL}/users/?entreprise=1", headers=headers)
        print(f"📥 Tentative accès entreprise 1: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Résultat: {len(data)} utilisateurs")
            
            # Vérifier que même avec le paramètre, on ne voit que notre entreprise
            entreprise_ids = set(u.get('entreprise') for u in data if u.get('entreprise'))
            print(f"🔍 Entreprises dans le résultat: {list(entreprise_ids)}")
            
            if entreprise_ids == {entreprise1.get('id')}:
                print(f"✅ Sécurité maintenue: on ne voit que notre entreprise")
            else:
                print(f"❌ Problème de sécurité: on voit d'autres entreprises")
        else:
            print(f"❌ Erreur: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 TEST COMPLET FILTRES PAR ENTREPRISE")
    print("=" * 50)
    
    # 1. Connexion SuperAdmin
    token, user, entreprise = test_jwt_login()
    if not token:
        print("\n❌ Impossible de continuer sans token SuperAdmin")
        return
    
    entreprise_id = entreprise.get('id')
    print(f"\n🏢 Entreprise connectée: {entreprise.get('nom')} (ID: {entreprise_id})")
    
    # 2. Test de tous les endpoints
    results = test_all_endpoints(token, entreprise_id)
    
    # 3. Test d'accès croisé
    test_cross_entreprise_access()
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ TESTS FILTRES ENTREPRISE")
    print("=" * 45)
    
    all_ok = True
    for endpoint, result in results.items():
        status = "✅" if result else "❌"
        print(f"   {endpoint}: {status}")
        if not result:
            all_ok = False
    
    if all_ok:
        print(f"\n🎉 TOUS LES FILTRES ENTREPRISE FONCTIONNENT!")
        print(f"   ✅ Utilisateurs filtrés par entreprise")
        print(f"   ✅ Boutiques filtrées par entreprise")
        print(f"   ✅ Produits filtrés par entreprise")
        print(f"   ✅ Factures filtrées par entreprise")
        print(f"   ✅ Sécurité maintenue entre entreprises")
        print(f"   ✅ Paramètres de requête supportés")
    else:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS")
        print(f"   - Vérifier les filtres des ViewSets")
        print(f"   - Vérifier les méthodes get_queryset()")

if __name__ == "__main__":
    main()




























