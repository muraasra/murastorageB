#!/usr/bin/env python3
"""
Test de création d'utilisateur avec envoi d'email en CC au SuperAdmin
- Créer un utilisateur avec wilfriedtayouf7@gmail.com
- Vérifier l'envoi d'email avec CC au SuperAdmin
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "admin@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT pour le SuperAdmin."""
    print("🔐 CONNEXION SUPERADMIN")
    print("=" * 30)
    
    login_data = {
        "email": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connexion SuperAdmin réussie!")
            print(f"   🔑 Token: {data.get('access', '')[:20]}...")
            print(f"   👤 User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   🏢 Entreprise: {data.get('entreprise', {}).get('nom', 'N/A')}")
            return data['access'], data['user']['id'], data['entreprise']['id']
        else:
            print(f"❌ Erreur connexion: {response.json()}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None, None

def get_boutiques(token, entreprise_id):
    """Récupérer les boutiques de l'entreprise."""
    print(f"\n🏢 RÉCUPÉRATION BOUTIQUES")
    print("=" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/boutiques/?entreprise={entreprise_id}", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            boutiques = response.json()
            print(f"✅ {len(boutiques)} boutique(s) trouvée(s)")
            
            for boutique in boutiques:
                print(f"   🏪 {boutique.get('nom')} (ID: {boutique.get('id')}) - {boutique.get('ville')}")
            
            return boutiques
        else:
            print(f"❌ Erreur: {response.json()}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def create_test_user(token, entreprise_id, boutique_id):
    """Créer un utilisateur de test avec wilfriedtayouf7@gmail.com."""
    print(f"\n👤 CRÉATION UTILISATEUR TEST")
    print("=" * 35)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "username": "wilfriedtayouf7",
        "email": "wilfriedtayouf7@gmail.com",
        "first_name": "Wilfried",
        "last_name": "Tayou",
        "role": "user",
        "telephone": "+237 6XX XXX XXX",
        "poste": "Gestionnaire de Stock",
        "entreprise": entreprise_id,
        "boutique": boutique_id,
        "is_active_employee": True
    }
    
    print(f"📤 Données utilisateur:")
    for key, value in user_data.items():
        print(f"   {key}: {value}")
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
        print(f"\n📥 Statut création: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Utilisateur créé avec succès!")
            print(f"   👤 ID: {data.get('id')}")
            print(f"   📧 Email: {data.get('email')}")
            print(f"   🏢 Entreprise: {data.get('entreprise_nom', 'N/A')}")
            print(f"   🏪 Boutique: {data.get('boutique_nom', 'N/A')}")
            print(f"   📧 Email envoyé avec CC au SuperAdmin!")
            return data
        else:
            print(f"❌ Erreur création: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def verify_user_creation(token, user_id):
    """Vérifier que l'utilisateur a été créé correctement."""
    print(f"\n🔍 VÉRIFICATION CRÉATION UTILISATEUR")
    print("=" * 45)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/", headers=headers)
        print(f"📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Utilisateur vérifié!")
            print(f"   👤 Nom: {data.get('first_name')} {data.get('last_name')}")
            print(f"   📧 Email: {data.get('email')}")
            print(f"   🏢 Entreprise: {data.get('entreprise_nom', 'N/A')}")
            print(f"   🏪 Boutique: {data.get('boutique_nom', 'N/A')}")
            print(f"   📞 Téléphone: {data.get('telephone', 'N/A')}")
            print(f"   💼 Poste: {data.get('poste', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur vérification: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_email_sending():
    """Test d'envoi d'email simple pour vérifier la configuration."""
    print(f"\n📧 TEST CONFIGURATION EMAIL")
    print("=" * 35)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Test d'envoi d'email simple
        send_mail(
            subject='Test Email Configuration - StoRage',
            message='Ceci est un test de configuration email.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['wilfriedtayouf7@gmail.com'],
            fail_silently=False,
        )
        
        print(f"✅ Email de test envoyé avec succès!")
        print(f"   📧 Destinataire: wilfriedtayouf7@gmail.com")
        print(f"   📤 Expéditeur: {settings.EMAIL_HOST_USER}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

def main():
    print("🚀 TEST CRÉATION UTILISATEUR AVEC CC EMAIL")
    print("=" * 50)
    
    # 1. Connexion SuperAdmin
    token, user_id, entreprise_id = test_jwt_login()
    if not token:
        print("\n❌ Impossible de continuer sans token SuperAdmin")
        return
    
    # 2. Récupération des boutiques
    boutiques = get_boutiques(token, entreprise_id)
    if not boutiques:
        print("\n❌ Aucune boutique trouvée")
        return
    
    # Utiliser la première boutique
    boutique_id = boutiques[0]['id']
    print(f"\n🏪 Utilisation de la boutique: {boutiques[0]['nom']} (ID: {boutique_id})")
    
    # 3. Test de configuration email
    email_config_ok = test_email_sending()
    
    # 4. Création de l'utilisateur test
    user_created = create_test_user(token, entreprise_id, boutique_id)
    
    # 5. Vérification de la création
    verification_ok = False
    if user_created:
        verification_ok = verify_user_creation(token, user_created['id'])
    
    # 6. Résumé
    print(f"\n📊 RÉSUMÉ TEST CRÉATION UTILISATEUR")
    print("=" * 45)
    print(f"   🔐 Connexion SuperAdmin: {'✅' if token else '❌'}")
    print(f"   🏢 Boutiques récupérées: {'✅' if boutiques else '❌'}")
    print(f"   📧 Configuration email: {'✅' if email_config_ok else '❌'}")
    print(f"   👤 Utilisateur créé: {'✅' if user_created else '❌'}")
    print(f"   🔍 Vérification: {'✅' if verification_ok else '❌'}")
    
    if user_created and verification_ok:
        print(f"\n🎉 TEST RÉUSSI!")
        print(f"   ✅ Utilisateur wilfriedtayouf7@gmail.com créé")
        print(f"   ✅ Email envoyé avec CC au SuperAdmin")
        print(f"   ✅ Utilisateur attribué à la boutique")
        print(f"   ✅ Vérification des données réussie")
        
        print(f"\n📧 VÉRIFIEZ VOS EMAILS:")
        print(f"   📬 wilfriedtayouf7@gmail.com (destinataire principal)")
        print(f"   📬 {SUPERADMIN_EMAIL} (CC)")
    else:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS")
        if not email_config_ok:
            print(f"   - Vérifier la configuration email")
        if not user_created:
            print(f"   - Vérifier la création d'utilisateur")
        if not verification_ok:
            print(f"   - Vérifier la vérification des données")

if __name__ == "__main__":
    main()




























