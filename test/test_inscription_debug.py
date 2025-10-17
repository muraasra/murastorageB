#!/usr/bin/env python3
"""
Script de debug spécifique pour l'API d'inscription
"""

import requests
import json
import time
from datetime import datetime

def test_inscription_with_debug():
    """Test détaillé de l'inscription avec debug"""
    print("🔍 DEBUG - Test d'inscription d'entreprise")
    print("=" * 50)
    
    # Données de test avec timestamp pour éviter les doublons
    timestamp = int(time.time())
    test_data = {
        "user": {
            "nom": "Debug",
            "prenom": "Test",
            "email": f"debug.test.{timestamp}@example.com",
            "telephone": "+237 6XX XX XX XX",
            "mot_de_passe": "debugpassword123",
            "role": "superadmin"
        },
        "nom": f"Entreprise Debug {timestamp}",
        "description": "Entreprise créée pour debug API",
        "secteur_activite": "Technologie et Informatique",
        "adresse": "123 Rue Debug",
        "ville": "Douala",
        "code_postal": "00000",
        "pays": "Cameroun",
        "telephone": "+237 2XX XX XX XX",
        "email": f"contact.debug.{timestamp}@example.com",
        "site_web": "https://www.debug-example.com",
        "numero_fiscal": "987654321",
        "nombre_employes": 3,
        "annee_creation": 2021,
        "pack_type": "basique",
        "pack_prix": 19,
        "pack_duree": "mensuel",
        "is_active": True
    }
    
    url = "http://127.0.0.1:8000/api/inscription/inscription/"
    headers = {'Content-Type': 'application/json'}
    
    print(f"📡 URL: {url}")
    print(f"📦 Données envoyées:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Test de connexion d'abord
        print("🔌 Test de connexion...")
        try:
            response = requests.get("http://127.0.0.1:8000/api/", timeout=5)
            print(f"✅ Serveur accessible (statut: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ Serveur non accessible - Démarrez avec: python manage.py runserver")
            return
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return
        
        print("\n📤 Envoi de la requête d'inscription...")
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        print(f"📄 Headers de la réponse:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"\n📄 Corps de la réponse:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"❌ Réponse non-JSON: {response.text}")
            return
        
        # Analyse de la réponse
        if response.status_code == 201:
            print("\n✅ SUCCÈS!")
            if response_data.get('success'):
                entreprise = response_data.get('entreprise', {})
                print(f"🏢 Entreprise créée: {entreprise.get('nom')}")
                print(f"🆔 ID Entreprise: {entreprise.get('id_entreprise')}")
                print(f"👤 Email utilisateur: {test_data['user']['email']}")
                print(f"📧 Email de vérification envoyé à: {test_data['user']['email']}")
            else:
                print(f"⚠️  Réponse indique un échec: {response_data.get('message')}")
        else:
            print(f"\n❌ ÉCHEC!")
            print(f"Statut: {response.status_code}")
            if 'message' in response_data:
                print(f"Message d'erreur: {response_data['message']}")
            
            # Debug des erreurs de validation
            if 'user' in response_data:
                print("Erreurs utilisateur:")
                for field, errors in response_data['user'].items():
                    print(f"  {field}: {errors}")
            
            if 'non_field_errors' in response_data:
                print(f"Erreurs générales: {response_data['non_field_errors']}")
                
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le serveur met trop de temps à répondre")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def test_validation_errors():
    """Test des erreurs de validation"""
    print("\n🔍 DEBUG - Test des erreurs de validation")
    print("=" * 50)
    
    # Test avec données invalides
    invalid_data = {
        "user": {
            "nom": "",  # Nom vide
            "prenom": "Test",
            "email": "email-invalide",  # Email invalide
            "telephone": "123",  # Téléphone invalide
            "mot_de_passe": "123",  # Mot de passe trop court
            "role": "superadmin"
        },
        "nom": "",  # Nom entreprise vide
        "description": "Test",
        "secteur_activite": "",  # Secteur vide
        "adresse": "",  # Adresse vide
        "ville": "",  # Ville vide
        "code_postal": "",
        "pays": "Cameroun",
        "telephone": "",
        "email": "email-invalide-entreprise",  # Email invalide
        "site_web": "site-invalide",  # URL invalide
        "numero_fiscal": "",
        "nombre_employes": -5,  # Nombre négatif
        "annee_creation": 1800,  # Année trop ancienne
        "pack_type": "invalid_pack",  # Pack invalide
        "pack_prix": -10,  # Prix négatif
        "pack_duree": "mensuel",
        "is_active": True
    }
    
    url = "http://127.0.0.1:8000/api/inscription/inscription/"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=invalid_data, headers=headers)
        print(f"📊 Statut: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Validation fonctionne - Erreurs détectées:")
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print(f"⚠️  Statut inattendu: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_inscription_with_debug()
    test_validation_errors()
