# test_mouvements_api.py
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User, MouvementStock
from rest_framework_simplejwt.tokens import RefreshToken

def test_mouvements_api():
    print("🔍 TEST DE L'API MOUVEMENTS DE STOCK")
    print("=" * 60)
    
    # Récupérer un utilisateur superadmin
    user = User.objects.filter(is_active=True, role='superadmin').first()
    if not user:
        print("❌ Aucun utilisateur superadmin trouvé")
        return
    
    print(f"👤 Utilisateur: {user.username}")
    print(f"🏢 Entreprise: {user.entreprise.nom}")
    print(f"🆔 ID Entreprise: {user.entreprise.id}")
    
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
    
    # Test 1: Mouvements sans filtre
    print(f"\n📡 TEST 1: Mouvements sans filtre")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/mouvements-stock/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mouvements récupérés: {len(data)}")
            for mouvement in data[:3]:
                print(f"   - {mouvement.get('produit_nom', 'N/A')} | {mouvement.get('type_mouvement', 'N/A')} | {mouvement.get('quantite', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Mouvements avec filtre entreprise
    print(f"\n📡 TEST 2: Mouvements avec filtre entreprise")
    print("-" * 40)
    
    try:
        response = requests.get(f'http://127.0.0.1:8000/api/mouvements-stock/?entrepot__entreprise={user.entreprise.id}', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mouvements récupérés: {len(data)}")
            for mouvement in data[:3]:
                print(f"   - {mouvement.get('produit_nom', 'N/A')} | {mouvement.get('type_mouvement', 'N/A')} | {mouvement.get('quantite', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Vérification directe en base
    print(f"\n🔍 VÉRIFICATION DIRECTE EN BASE")
    print("-" * 40)
    
    try:
        # Mouvements pour l'entreprise de l'utilisateur
        mouvements_entreprise = MouvementStock.objects.filter(entrepot__entreprise=user.entreprise)
        print(f"📊 Mouvements pour l'entreprise: {mouvements_entreprise.count()}")
        
        for mouvement in mouvements_entreprise[:3]:
            print(f"   - {mouvement.produit.nom} | {mouvement.type_mouvement} | {mouvement.quantite} | {mouvement.entrepot.nom}")
        
        # Total des mouvements
        total_mouvements = MouvementStock.objects.count()
        print(f"📊 Total des mouvements en base: {total_mouvements}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
    
    # Test 4: Test des permissions
    print(f"\n🔍 TEST DES PERMISSIONS")
    print("-" * 40)
    
    try:
        from core.permissions import IsAdminOrSuperAdmin
        permission = IsAdminOrSuperAdmin()
        
        # Simuler une requête
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        mock_request = MockRequest(user)
        has_permission = permission.has_permission(mock_request, None)
        print(f"✅ Permission IsAdminOrSuperAdmin: {has_permission}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test des permissions: {str(e)}")

if __name__ == "__main__":
    test_mouvements_api()






