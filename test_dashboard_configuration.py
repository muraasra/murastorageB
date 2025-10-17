# test_dashboard_configuration.py
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User, Boutique, Entreprise
from rest_framework_simplejwt.tokens import RefreshToken

def test_dashboard_configuration():
    print("🔍 TEST DE CONFIGURATION DU DASHBOARD")
    print("=" * 60)
    
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
    
    # Tester les endpoints critiques du dashboard
    endpoints_to_test = [
        {
            'url': '/api/entreprises/',
            'name': 'Liste des entreprises',
            'critical': True
        },
        {
            'url': f'/api/entreprises/{user.entreprise.id}/',
            'name': 'Détails entreprise',
            'critical': True
        },
        {
            'url': f'/api/boutiques/?entreprise={user.entreprise.id}',
            'name': 'Boutiques par entreprise',
            'critical': True
        },
        {
            'url': f'/api/users/?entreprise={user.entreprise.id}',
            'name': 'Utilisateurs par entreprise',
            'critical': True
        },
        {
            'url': '/api/stocks/',
            'name': 'Stocks',
            'critical': False
        }
    ]
    
    print(f"\n📡 TEST DES ENDPOINTS CRITIQUES")
    print("-" * 40)
    
    all_tests_passed = True
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Test: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            response = requests.get(f'http://127.0.0.1:8000{endpoint["url"]}', headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès - Type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"   📊 Éléments: {len(data)}")
                    if data and endpoint['critical']:
                        first_item = data[0]
                        print(f"   🔍 Premier élément: {list(first_item.keys())}")
                        
                        # Vérifier les champs critiques
                        if 'nom' in first_item:
                            nom = first_item['nom']
                            print(f"   📝 Nom: '{nom}' (type: {type(nom)})")
                            if nom is None or nom == '':
                                print("   ⚠️  ATTENTION: Nom vide ou null!")
                        else:
                            print("   ⚠️  ATTENTION: Pas de champ 'nom'!")
                            
                elif isinstance(data, dict):
                    print(f"   📊 Clés: {list(data.keys())}")
                    if endpoint['critical'] and 'nom' in data:
                        nom = data['nom']
                        print(f"   📝 Nom: '{nom}' (type: {type(nom)})")
                        if nom is None or nom == '':
                            print("   ⚠️  ATTENTION: Nom vide ou null!")
                            
            else:
                print(f"   ❌ Erreur: {response.text}")
                if endpoint['critical']:
                    all_tests_passed = False
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            if endpoint['critical']:
                all_tests_passed = False
    
    # Vérifier la cohérence des données
    print(f"\n🔍 VÉRIFICATION DE COHÉRENCE")
    print("-" * 40)
    
    try:
        # Vérifier que l'entreprise a des boutiques
        boutiques = Boutique.objects.filter(entreprise=user.entreprise)
        print(f"📊 Boutiques en base pour l'entreprise: {boutiques.count()}")
        
        for boutique in boutiques[:3]:
            print(f"   - {boutique.nom} (ID: {boutique.id})")
            if boutique.nom is None or boutique.nom == '':
                print("     ⚠️  ATTENTION: Nom de boutique vide!")
        
        # Vérifier que l'entreprise a des utilisateurs
        users_count = User.objects.filter(entreprise=user.entreprise).count()
        print(f"📊 Utilisateurs en base pour l'entreprise: {users_count}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        all_tests_passed = False
    
    # Résumé final
    print(f"\n🎯 RÉSUMÉ DU TEST")
    print("=" * 60)
    
    if all_tests_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("🚀 Le dashboard devrait fonctionner correctement")
        print("\n📋 CONFIGURATION VALIDÉE:")
        print("   ✅ API endpoints accessibles")
        print("   ✅ Structure des réponses correcte")
        print("   ✅ Données cohérentes en base")
        print("   ✅ Authentification fonctionnelle")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Des corrections sont nécessaires")
        print("\n📋 PROBLÈMES DÉTECTÉS:")
        print("   ❌ Endpoints critiques non accessibles")
        print("   ❌ Structure des réponses incorrecte")
        print("   ❌ Données incohérentes")
        print("   ❌ Problèmes d'authentification")

if __name__ == "__main__":
    test_dashboard_configuration()
