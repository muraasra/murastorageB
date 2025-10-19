# test_dashboard_fix.py
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User, Boutique, Entreprise
from rest_framework_simplejwt.tokens import RefreshToken

def test_dashboard_data():
    print("🔍 TEST DES DONNÉES DU DASHBOARD")
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
    
    # Tester les endpoints du dashboard
    endpoints = [
        '/api/boutiques/',
        '/api/users/',
        '/api/entreprises/',
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
                
                if isinstance(data, list):
                    print(f"✅ Liste de {len(data)} éléments")
                    if data:
                        first_item = data[0]
                        print(f"   - Premier élément: {list(first_item.keys())}")
                        
                        # Vérifier les champs critiques
                        if 'nom' in first_item:
                            nom = first_item['nom']
                            print(f"   - Nom: '{nom}' (type: {type(nom)})")
                            if nom is None:
                                print("   ⚠️  ATTENTION: Le nom est null!")
                        else:
                            print("   ⚠️  ATTENTION: Pas de champ 'nom'!")
                            
                else:
                    print(f"📋 Réponse de type: {type(data)}")
                    print(f"   - Contenu: {str(data)[:100]}...")
                    
            else:
                print(f"❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

    # Vérifier directement en base
    print(f"\n🔍 VÉRIFICATION DIRECTE EN BASE")
    print("-" * 30)
    
    boutiques = Boutique.objects.all()
    print(f"📊 Boutiques en base: {boutiques.count()}")
    
    for boutique in boutiques[:3]:  # Afficher les 3 premières
        print(f"   - ID: {boutique.id}, Nom: '{boutique.nom}' (type: {type(boutique.nom)})")
        if boutique.nom is None:
            print("     ⚠️  ATTENTION: Le nom est null en base!")
    
    users = User.objects.all()
    print(f"📊 Utilisateurs en base: {users.count()}")
    
    entreprises = Entreprise.objects.all()
    print(f"📊 Entreprises en base: {entreprises.count()}")

if __name__ == "__main__":
    test_dashboard_data()






