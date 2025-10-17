# test_api_structure.py
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_api_structure():
    print("🔍 TEST DE LA STRUCTURE DES API")
    print("=" * 50)
    
    # Récupérer un utilisateur admin de test
    user = User.objects.filter(is_active=True, role__in=['admin', 'superadmin']).first()
    if not user:
        print("❌ Aucun utilisateur admin actif trouvé")
        return
    
    print(f"👤 Utilisateur de test: {user.username} ({user.email})")
    print(f"🏢 Entreprise: {user.entreprise.nom if user.entreprise else 'Aucune'}")
    
    # Générer un token JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"🔑 Token généré: {access_token[:20]}...")
    
    # Headers pour les requêtes
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Tester différents endpoints
    endpoints = [
        '/api/produits/',
        '/api/stocks/',
        '/api/categories/',
        '/api/boutiques/',
        '/api/fournisseurs/',
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Test de {endpoint}")
        print("-" * 30)
        
        try:
            response = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Type de réponse: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"Clés disponibles: {list(data.keys())}")
                    
                    # Vérifier si c'est une réponse paginée
                    if 'results' in data:
                        print(f"✅ Réponse paginée détectée")
                        print(f"   - Nombre d'éléments: {len(data['results'])}")
                        print(f"   - Total: {data.get('count', 'N/A')}")
                        print(f"   - Page suivante: {data.get('next', 'N/A')}")
                        print(f"   - Page précédente: {data.get('previous', 'N/A')}")
                        
                        # Afficher le premier élément
                        if data['results']:
                            first_item = data['results'][0]
                            print(f"   - Premier élément: {list(first_item.keys())}")
                    else:
                        print(f"📋 Réponse directe (non paginée)")
                        if isinstance(data, list):
                            print(f"   - Nombre d'éléments: {len(data)}")
                            if data:
                                print(f"   - Premier élément: {list(data[0].keys())}")
                        else:
                            print(f"   - Contenu: {str(data)[:100]}...")
                else:
                    print(f"📋 Réponse de type: {type(data)}")
                    print(f"   - Contenu: {str(data)[:100]}...")
                    
            else:
                print(f"❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_api_structure()
