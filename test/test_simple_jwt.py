#!/usr/bin/env python3
"""
Test simple de l'authentification JWT
"""

import requests
import json

def test_simple_jwt():
    """Test simple de JWT"""
    print("🔐 Test simple JWT")
    print("=" * 30)
    
    # Données de connexion
    login_data = {
        "username": "test.auth.1759282506@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Test JWT
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/jwt/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JWT fonctionne!")
            print(f"Access token: {data.get('access', '')[:50]}...")
            print(f"Refresh token: {data.get('refresh', '')[:50]}...")
            print(f"Nombre de champs: {len(data)}")
            
            # Afficher les clés principales
            print("\nClés principales:")
            for key in data.keys():
                print(f"  - {key}")
                
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_jwt()
