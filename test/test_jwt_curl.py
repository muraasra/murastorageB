#!/usr/bin/env python3
"""
Test JWT avec curl via subprocess
"""

import subprocess
import json
import sys

def test_jwt_with_curl():
    """Test JWT avec curl"""
    print("🔐 Test JWT avec curl")
    print("=" * 30)
    
    # Données de connexion
    login_data = {
        "username": "test.auth.1759282506@example.com",
        "password": "testpassword123"
    }
    
    # Commande curl
    curl_cmd = [
        "curl",
        "-X", "POST",
        "http://127.0.0.1:8000/api/auth/jwt/login/",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(login_data),
        "-s"  # Silent mode
    ]
    
    try:
        print("📤 Envoi de la requête...")
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        
        print(f"📊 Code de retour: {result.returncode}")
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                print("✅ JWT fonctionne!")
                print(f"Access token: {response_data.get('access', '')[:50]}...")
                print(f"Refresh token: {response_data.get('refresh', '')[:50]}...")
                print(f"Nombre de champs: {len(response_data)}")
                
                # Afficher les clés principales
                print("\nClés principales:")
                for key in response_data.keys():
                    print(f"  - {key}")
                    
            except json.JSONDecodeError:
                print("❌ Réponse non-JSON:")
                print(result.stdout)
        else:
            print(f"❌ Erreur curl: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout - Le serveur ne répond pas")
    except FileNotFoundError:
        print("❌ curl non trouvé - Installez curl ou utilisez une autre méthode")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_token_with_curl():
    """Test Token avec curl pour comparaison"""
    print(f"\n🔑 Test Token avec curl (comparaison)")
    print("=" * 40)
    
    login_data = {
        "username": "test.auth.1759282506@example.com",
        "password": "testpassword123"
    }
    
    curl_cmd = [
        "curl",
        "-X", "POST",
        "http://127.0.0.1:8000/api/auth/login/",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(login_data),
        "-s"
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                print("✅ Token fonctionne!")
                print(f"Token: {response_data.get('token', '')[:50]}...")
                print(f"Nombre de champs: {len(response_data)}")
            except json.JSONDecodeError:
                print("❌ Réponse non-JSON:")
                print(result.stdout)
        else:
            print(f"❌ Erreur curl: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_jwt_with_curl()
    test_token_with_curl()
