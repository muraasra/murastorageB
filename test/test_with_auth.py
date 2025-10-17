#!/usr/bin/env python3
"""
Script de test avec authentification
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

def test_auth_and_apis():
    """Test complet avec authentification"""
    print("🔐 Test avec authentification")
    print("=" * 50)
    
    # 1. Créer une entreprise pour avoir un utilisateur
    timestamp = int(time.time())
    inscription_data = {
        "user": {
            "nom": "Test",
            "prenom": "Auth",
            "email": f"test.auth.{timestamp}@example.com",
            "telephone": "+237 6XX XX XX XX",
            "mot_de_passe": "testpassword123",
            "role": "superadmin"
        },
        "nom": f"Entreprise Auth {timestamp}",
        "description": "Entreprise pour test auth",
        "secteur_activite": "Technologie et Informatique",
        "adresse": "123 Rue Auth",
        "ville": "Douala",
        "code_postal": "00000",
        "pays": "Cameroun",
        "telephone": "+237 2XX XX XX XX",
        "email": f"contact.auth.{timestamp}@example.com",
        "site_web": "https://www.auth-example.com",
        "numero_fiscal": "123456789",
        "nombre_employes": 5,
        "annee_creation": 2020,
        "pack_type": "professionnel",
        "pack_prix": 49,
        "pack_duree": "mensuel",
        "is_active": True
    }
    
    print("1️⃣ Création d'entreprise...")
    try:
        response = requests.post(f"{BASE_URL}/inscription/inscription/", json=inscription_data, headers=HEADERS)
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print(f"✅ Entreprise créée: {data['entreprise']['nom']}")
                email = inscription_data['user']['email']
            else:
                print(f"❌ Échec création: {data.get('message')}")
                return
        else:
            print(f"❌ Erreur création: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # 2. Se connecter avec l'utilisateur créé
    print("\n2️⃣ Connexion utilisateur...")
    login_data = {
        "username": email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data['token']
            user_id = auth_data['user_id']
            print(f"✅ Connexion réussie - Token: {token[:20]}...")
            print(f"👤 Utilisateur: {auth_data['username']}")
            print(f"🏢 Entreprise: {auth_data['entreprise_nom']}")
        else:
            print(f"❌ Échec connexion: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # Headers avec authentification
    auth_headers = HEADERS.copy()
    auth_headers['Authorization'] = f'Token {token}'
    
    # 3. Tester les APIs avec authentification
    print("\n3️⃣ Test des APIs authentifiées...")
    
    # Test entreprises
    try:
        response = requests.get(f"{BASE_URL}/entreprises/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Entreprises: {len(data)} trouvées")
        else:
            print(f"❌ Entreprises: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur entreprises: {e}")
    
    # Test boutiques
    try:
        response = requests.get(f"{BASE_URL}/boutiques/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Boutiques: {len(data)} trouvées")
            if data:
                boutique_id = data[0]['id']
                print(f"   Première boutique: {data[0]['nom']}")
        else:
            print(f"❌ Boutiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur boutiques: {e}")
    
    # Test produits
    try:
        response = requests.get(f"{BASE_URL}/produits/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Produits: {len(data)} trouvés")
        else:
            print(f"❌ Produits: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
    
    # Test création produit
    if 'boutique_id' in locals():
        print("\n4️⃣ Création d'un produit...")
        produit_data = {
            "nom": f"Produit Test {timestamp}",
            "description": "Produit créé par test API",
            "categorie": "informatique",
            "prix_achat": 100.0,
            "prix_vente": 150.0,
            "stock_actuel": 10,
            "stock_minimum": 5,
            "boutique": boutique_id,
            "marque": "Test Brand",
            "modele": "Test Model",
            "processeur": "Intel i5",
            "ram": "8GB",
            "stockage": "256GB SSD",
            "systeme_exploitation": "Windows 10",
            "annee": 2023
        }
        
        try:
            response = requests.post(f"{BASE_URL}/produits/", json=produit_data, headers=auth_headers)
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Produit créé: {data['nom']} (ID: {data['id']})")
            else:
                print(f"❌ Création produit: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erreur création produit: {e}")
    
    # Test factures
    try:
        response = requests.get(f"{BASE_URL}/factures/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Factures: {len(data)} trouvées")
        else:
            print(f"❌ Factures: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur factures: {e}")
    
    # Test journaux
    try:
        response = requests.get(f"{BASE_URL}/journaux/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Journaux: {len(data)} entrées trouvées")
        else:
            print(f"❌ Journaux: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur journaux: {e}")
    
    # Test utilisateurs
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Utilisateurs: {len(data)} trouvés")
        else:
            print(f"❌ Utilisateurs: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur utilisateurs: {e}")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_auth_and_apis()
