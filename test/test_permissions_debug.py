#!/usr/bin/env python3
"""
Script de debug des permissions
"""

import requests
import json
import time

def test_permissions_debug():
    """Test détaillé des permissions"""
    print("🔐 DEBUG - Test des permissions")
    print("=" * 50)
    
    # Utiliser un utilisateur existant avec entreprise
    email = "test.auth.1759282506@example.com"
    password = "testpassword123"
    
    # 1. Connexion
    print("1️⃣ Connexion...")
    login_data = {"username": email, "password": password}
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/auth/login/", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data['token']
            print(f"✅ Connexion réussie")
            print(f"   Token: {token[:20]}...")
            print(f"   Rôle: {auth_data['role']}")
            print(f"   Entreprise: {auth_data['entreprise_nom']}")
            print(f"   Boutique: {auth_data['boutique_nom']}")
        else:
            print(f"❌ Échec connexion: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # Headers avec authentification
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {token}'
    }
    
    # 2. Test des endpoints un par un
    endpoints = [
        ("/entreprises/", "Entreprises"),
        ("/boutiques/", "Boutiques"),
        ("/produits/", "Produits"),
        ("/factures/", "Factures"),
        ("/journaux/", "Journaux"),
        ("/users/", "Utilisateurs"),
    ]
    
    print(f"\n2️⃣ Test des endpoints:")
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8000/api{endpoint}", headers=headers)
            print(f"   {name}: {response.status_code}")
            
            if response.status_code == 403:
                print(f"      ❌ Forbidden - Détails: {response.text}")
            elif response.status_code == 200:
                data = response.json()
                print(f"      ✅ Succès - {len(data)} éléments")
            else:
                print(f"      ⚠️  Statut inattendu: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    # 3. Test de création d'un produit
    print(f"\n3️⃣ Test création produit...")
    
    # D'abord récupérer une boutique
    try:
        boutiques_response = requests.get("http://127.0.0.1:8000/api/boutiques/", headers=headers)
        if boutiques_response.status_code == 200:
            boutiques = boutiques_response.json()
            if boutiques:
                boutique_id = boutiques[0]['id']
                print(f"   Boutique sélectionnée: {boutiques[0]['nom']} (ID: {boutique_id})")
            else:
                print("   ❌ Aucune boutique disponible")
                return
        else:
            print(f"   ❌ Erreur récupération boutiques: {boutiques_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    produit_data = {
        "nom": f"Produit Debug {int(time.time())}",
        "description": "Produit créé pour debug permissions",
        "category": "ordinateur",
        "prix_achat": 100.0,
        "prix": 150.0,
        "quantite": 10,
        "boutique": boutique_id,
        "marque": "Debug Brand",
        "modele": "Debug Model",
        "processeur": "Intel i5",
        "ram": "8GB",
        "stockage": "256GB SSD",
        "systeme_exploitation": "Windows 10",
        "annee": 2023
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/produits/", json=produit_data, headers=headers)
        print(f"   Création produit: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"      ✅ Produit créé: {data['nom']} (ID: {data['id']})")
        elif response.status_code == 403:
            print(f"      ❌ Forbidden - Détails: {response.text}")
        else:
            print(f"      ⚠️  Statut inattendu: {response.text}")
            
    except Exception as e:
        print(f"      ❌ Erreur: {e}")

if __name__ == "__main__":
    test_permissions_debug()
