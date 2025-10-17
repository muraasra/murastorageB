# test_useapi_structure.py
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def test_useapi_structure():
    print("🔍 TEST DE LA STRUCTURE useApi")
    print("=" * 50)
    
    # Récupérer un utilisateur superadmin
    user = User.objects.filter(is_active=True, role='superadmin').first()
    if not user:
        print("❌ Aucun utilisateur superadmin trouvé")
        return
    
    print(f"👤 Utilisateur superadmin: {user.username} ({user.email})")
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
    
    # Tester l'endpoint des boutiques
    endpoint = f'/api/boutiques/?entreprise={user.entreprise.id}'
    print(f"\n📡 Test de {endpoint}")
    print("-" * 30)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Type de réponse: {type(data)}")
            
            if isinstance(data, list):
                print(f"✅ Liste de {len(data)} éléments")
                if data:
                    first_item = data[0]
                    print(f"   - Premier élément: {list(first_item.keys())}")
                    print(f"   - Structure complète: {json.dumps(first_item, indent=2)}")
            else:
                print(f"❌ Réponse n'est pas une liste: {type(data)}")
                print(f"   - Contenu: {json.dumps(data, indent=2)}")
                
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    # Tester aussi l'endpoint des utilisateurs
    endpoint = f'/api/users/?entreprise={user.entreprise.id}'
    print(f"\n📡 Test de {endpoint}")
    print("-" * 30)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Type de réponse: {type(data)}")
            
            if isinstance(data, list):
                print(f"✅ Liste de {len(data)} éléments")
                if data:
                    first_item = data[0]
                    print(f"   - Premier élément: {list(first_item.keys())}")
            else:
                print(f"❌ Réponse n'est pas une liste: {type(data)}")
                print(f"   - Contenu: {json.dumps(data, indent=2)}")
                
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_useapi_structure()



