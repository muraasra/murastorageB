#!/usr/bin/env python3
"""
Debug de la création d'utilisateur
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def get_auth_token():
    """Obtenir un token d'authentification"""
    login_data = {
        "username": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Erreur connexion: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def debug_user_creation():
    """Debug de la création d'utilisateur"""
    print("🔍 Debug de la création d'utilisateur...")
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # D'abord récupérer une boutique
    try:
        response = requests.get(f"{BASE_URL}/boutiques/", headers=headers)
        if response.status_code == 200:
            boutiques = response.json()
            if boutiques:
                boutique_id = boutiques[0]['id']
                print(f"🏪 Boutique sélectionnée: {boutiques[0]['nom']} (ID: {boutique_id})")
            else:
                print("❌ Aucune boutique disponible")
                return
        else:
            print(f"❌ Erreur récupération boutiques: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Créer un utilisateur avec des données complètes
    user_data = {
        "username": f"debuguser{int(time.time())}@test.com",
        "first_name": "Debug",
        "last_name": "User",
        "email": f"debuguser{int(time.time())}@test.com",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Debug Poste",
        "role": "user",
        "boutique": boutique_id,
        "send_email": False  # Pas d'email pour debug
    }
    
    print(f"📤 Données envoyées: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        print(f"📥 Statut réponse: {response.status_code}")
        print(f"📥 Réponse complète: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            user_info = data.get('user', {})
            print(f"✅ Utilisateur créé avec succès!")
            print(f"   ID: {user_info.get('id')}")
            print(f"   Username: {user_info.get('username')}")
            print(f"   Email: {user_info.get('email')}")
            print(f"   First Name: {user_info.get('first_name')}")
            print(f"   Last Name: {user_info.get('last_name')}")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Entreprise: {user_info.get('entreprise')}")
            print(f"   Boutique: {user_info.get('boutique')}")
            print(f"   Entreprise Nom: {user_info.get('entreprise_nom')}")
            print(f"   Boutique Nom: {user_info.get('boutique_nom')}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    debug_user_creation()




























