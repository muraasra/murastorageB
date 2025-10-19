# test_dashboard_data.py
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
    print("=" * 60)
    
    # Récupérer un utilisateur superadmin
    user = User.objects.filter(is_active=True, role='superadmin').first()
    if not user:
        print("❌ Aucun utilisateur superadmin trouvé")
        return
    
    print(f"👤 Utilisateur superadmin: {user.username} ({user.email})")
    print(f"🏢 Entreprise: {user.entreprise.nom if user.entreprise else 'Aucune'}")
    print(f"🆔 ID Entreprise: {user.entreprise.id if user.entreprise else 'N/A'}")
    
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
    
    # Test 1: Détails de l'entreprise
    print(f"\n📡 TEST 1: Détails de l'entreprise")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/entreprises/{user.entreprise.id}/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données entreprise récupérées")
            print(f"   - Nom: {data.get('nom', 'N/A')}")
            print(f"   - Boutiques: {len(data.get('boutiques', []))}")
            print(f"   - Utilisateurs: {len(data.get('users', []))}")
            
            if 'boutiques' in data:
                print(f"   - Boutiques détaillées: {[b.get('nom', 'N/A') for b in data['boutiques']]}")
            if 'users' in data:
                print(f"   - Utilisateurs détaillés: {[u.get('username', 'N/A') for u in data['users']]}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Boutiques par entreprise
    print(f"\n📡 TEST 2: Boutiques par entreprise")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/boutiques/?entreprise={user.entreprise.id}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Boutiques récupérées: {len(data)}")
            for boutique in data:
                print(f"   - {boutique.get('nom', 'N/A')} (ID: {boutique.get('id', 'N/A')})")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Utilisateurs par entreprise
    print(f"\n📡 TEST 3: Utilisateurs par entreprise")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/users/?entreprise={user.entreprise.id}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Utilisateurs récupérés: {len(data)}")
            for user_data in data:
                print(f"   - {user_data.get('username', 'N/A')} ({user_data.get('role', 'N/A')})")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 4: Mouvements de stock
    print(f"\n📡 TEST 4: Mouvements de stock")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/mouvements-stock/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mouvements récupérés: {len(data)}")
            for mouvement in data[:3]:  # Afficher les 3 premiers
                print(f"   - {mouvement.get('produit_nom', 'N/A')} - {mouvement.get('type_mouvement', 'N/A')} - {mouvement.get('quantite', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Vérification directe en base
    print(f"\n🔍 VÉRIFICATION DIRECTE EN BASE")
    print("-" * 40)
    
    try:
        boutiques_count = Boutique.objects.filter(entreprise=user.entreprise).count()
        users_count = User.objects.filter(entreprise=user.entreprise).count()
        
        print(f"📊 Boutiques en base pour l'entreprise: {boutiques_count}")
        print(f"📊 Utilisateurs en base pour l'entreprise: {users_count}")
        
        # Lister les boutiques
        boutiques = Boutique.objects.filter(entreprise=user.entreprise)
        for boutique in boutiques:
            print(f"   - {boutique.nom} (ID: {boutique.id})")
        
        # Lister les utilisateurs
        users = User.objects.filter(entreprise=user.entreprise)
        for user_obj in users:
            print(f"   - {user_obj.username} ({user_obj.role})")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")

if __name__ == "__main__":
    test_dashboard_data()






