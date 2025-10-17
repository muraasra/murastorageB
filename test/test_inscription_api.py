#!/usr/bin/env python3
"""
Script de test pour l'API d'inscription d'entreprise
"""

import requests
import json

# URL de l'API
API_URL = "http://127.0.0.1:8000/api/inscription/inscription/"

# Données de test
test_data = {
    "user": {
        "nom": "Test",
        "prenom": "User",
        "email": "test.user@example.com",
        "telephone": "+237 6XX XX XX XX",
        "mot_de_passe": "testpassword123",
        "role": "superadmin"
    },
    "nom": "Entreprise Test",
    "description": "Une entreprise de test",
    "secteur_activite": "Technologie et Informatique",
    "adresse": "123 Rue Test",
    "ville": "Douala",
    "code_postal": "00000",
    "pays": "Cameroun",
    "telephone": "+237 2XX XX XX XX",
    "email": "contact@entreprise-test.com",
    "site_web": "https://www.entreprise-test.com",
    "numero_fiscal": "123456789",
    "nombre_employes": 5,
    "annee_creation": 2020,
    "pack_type": "professionnel",
    "pack_prix": 49,
    "pack_duree": "mensuel",
    "is_active": True
}

def test_inscription_api():
    """Test de l'API d'inscription"""
    print("🧪 Test de l'API d'inscription d'entreprise")
    print("=" * 50)
    
    print(f"📡 URL: {API_URL}")
    print(f"📦 Données envoyées:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Envoyer la requête
        response = requests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        print(f"📄 Réponse:")
        
        if response.status_code == 201:
            print("✅ Succès!")
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print("❌ Erreur!")
            print(f"Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Le serveur n'est pas démarré")
        print("💡 Démarrez le serveur avec: python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_inscription_api()
