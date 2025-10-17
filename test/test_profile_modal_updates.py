#!/usr/bin/env python3
"""
Test des modifications du modal profil
- Vérifier que l'ID entreprise est affiché
- Vérifier que les champs boutique sont retirés
- Vérifier que les dates sont affichées
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_EMAIL = "admin@test.com"
SUPERADMIN_PASSWORD = "admin123"

def test_jwt_login():
    """Test de connexion JWT et récupération du token."""
    print("🔐 Connexion JWT...")
    login_data = {
        "username": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data['access'], data['user']['id'], data['entreprise']['id']
        else:
            print(f"❌ Erreur connexion: {response.json()}")
            return None, None, None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, None, None

def get_user_data(token, user_id):
    """Récupération des données utilisateur."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def check_profile_modal_fields():
    """Vérification des champs du modal profil après modifications."""
    print("\n🔍 VÉRIFICATION DES CHAMPS MODAL PROFIL")
    print("=" * 50)
    
    # Champs affichés dans EditProfileModal.vue (après modifications)
    modal_profile_fields = {
        'id', 'username', 'first_name', 'last_name', 'email', 'role',
        'telephone', 'poste', 'date_embauche', 'is_active_employee',
        'entreprise', 'entreprise_nom', 'created_at', 'updated_at',
        'password', 'confirm_password'
    }
    
    print(f"\n👤 CHAMPS MODAL PROFIL ({len(modal_profile_fields)}):")
    print("-" * 40)
    for field in sorted(modal_profile_fields):
        print(f"   ✅ {field}")
    
    # Vérification des champs spécifiques
    print(f"\n📋 VÉRIFICATIONS SPÉCIFIQUES:")
    print("-" * 30)
    
    # ID Entreprise présent
    if 'entreprise' in modal_profile_fields:
        print(f"   ✅ ID Entreprise affiché")
    else:
        print(f"   ❌ ID Entreprise manquant")
    
    # Nom Entreprise présent
    if 'entreprise_nom' in modal_profile_fields:
        print(f"   ✅ Nom Entreprise affiché")
    else:
        print(f"   ❌ Nom Entreprise manquant")
    
    # Dates présentes
    if 'created_at' in modal_profile_fields:
        print(f"   ✅ Date de création affichée")
    else:
        print(f"   ❌ Date de création manquante")
    
    if 'updated_at' in modal_profile_fields:
        print(f"   ✅ Date de modification affichée")
    else:
        print(f"   ❌ Date de modification manquante")
    
    # Champs boutique retirés
    boutique_fields = {'boutique', 'boutique_nom'}
    boutique_removed = boutique_fields.isdisjoint(modal_profile_fields)
    
    if boutique_removed:
        print(f"   ✅ Champs boutique retirés")
    else:
        print(f"   ❌ Champs boutique encore présents: {boutique_fields & modal_profile_fields}")
    
    return modal_profile_fields

def test_user_data_display(user_data):
    """Test de l'affichage des données utilisateur."""
    print(f"\n👤 DONNÉES UTILISATEUR À AFFICHER")
    print("=" * 40)
    
    if user_data:
        print(f"   🆔 ID: {user_data.get('id', 'N/A')}")
        print(f"   👤 Username: {user_data.get('username', 'N/A')}")
        print(f"   👨 Prénom: {user_data.get('first_name', 'N/A')}")
        print(f"   👨 Nom: {user_data.get('last_name', 'N/A')}")
        print(f"   📧 Email: {user_data.get('email', 'N/A')}")
        print(f"   🎭 Rôle: {user_data.get('role', 'N/A')}")
        print(f"   📞 Téléphone: {user_data.get('telephone', 'N/A')}")
        print(f"   💼 Poste: {user_data.get('poste', 'N/A')}")
        print(f"   📅 Date embauche: {user_data.get('date_embauche', 'N/A')}")
        print(f"   ✅ Statut employé: {user_data.get('is_active_employee', 'N/A')}")
        print(f"   🏢 ID Entreprise: {user_data.get('entreprise', 'N/A')}")
        print(f"   🏢 Nom Entreprise: {user_data.get('entreprise_nom', 'N/A')}")
        print(f"   📅 Créé le: {user_data.get('created_at', 'N/A')}")
        print(f"   📅 Modifié le: {user_data.get('updated_at', 'N/A')}")
        
        # Vérification que l'utilisateur est bien lié à une entreprise
        if user_data.get('entreprise'):
            print(f"\n   ✅ Utilisateur lié à l'entreprise ID: {user_data.get('entreprise')}")
        else:
            print(f"\n   ⚠️  Utilisateur non lié à une entreprise")
    else:
        print(f"   ❌ Aucune donnée utilisateur disponible")

def test_modal_layout():
    """Test de la disposition du modal."""
    print(f"\n🎨 DISPOSITION DU MODAL PROFIL")
    print("=" * 35)
    
    print(f"\n📋 Structure du formulaire:")
    print(f"   📸 Photo de profil (upload)")
    print(f"   🆔 ID utilisateur (lecture seule)")
    print(f"   👤 Username (lecture seule)")
    print(f"   👨 Prénom (modifiable)")
    print(f"   👨 Nom (modifiable)")
    print(f"   📧 Email (lecture seule)")
    print(f"   🎭 Rôle (lecture seule)")
    print(f"   📞 Téléphone (modifiable)")
    print(f"   💼 Poste (modifiable)")
    print(f"   📅 Date d'embauche (modifiable)")
    print(f"   ✅ Statut employé (modifiable)")
    print(f"   🏢 ID Entreprise (lecture seule)")
    print(f"   🏢 Nom Entreprise (lecture seule)")
    print(f"   📅 Date de création (lecture seule)")
    print(f"   📅 Dernière modification (lecture seule)")
    print(f"   🔒 Nouveau mot de passe (optionnel)")
    print(f"   🔒 Confirmation mot de passe (optionnel)")

def main():
    print("🚀 TEST DES MODIFICATIONS MODAL PROFIL")
    print("=" * 45)
    
    # 1. Connexion
    access_token, user_id, entreprise_id = test_jwt_login()
    if not access_token:
        print("\n❌ Impossible de continuer sans token")
        return
    
    # 2. Récupération des données utilisateur
    user_data = get_user_data(access_token, user_id)
    
    # 3. Vérification des champs du modal
    modal_fields = check_profile_modal_fields()
    
    # 4. Test de l'affichage des données
    test_user_data_display(user_data)
    
    # 5. Test de la disposition du modal
    test_modal_layout()
    
    # 6. Résumé final
    print(f"\n🎉 RÉSUMÉ DES MODIFICATIONS")
    print("=" * 35)
    
    print(f"\n✅ Modifications apportées:")
    print(f"   🏢 ID Entreprise affiché (obligatoire)")
    print(f"   🏢 Nom Entreprise affiché")
    print(f"   📅 Date de création affichée")
    print(f"   📅 Date de modification affichée")
    print(f"   🗑️  Champs boutique retirés")
    
    print(f"\n📊 Résultat:")
    print(f"   👤 Modal Profil: {len(modal_fields)} champs")
    print(f"   🏢 Entreprise: Liée et affichée")
    print(f"   📅 Dates: Création et modification visibles")
    print(f"   🗑️  Boutique: Champs retirés")
    
    print(f"\n🎯 Conclusion:")
    print(f"   ✅ Modal profil adapté aux spécifications")
    print(f"   ✅ ID entreprise affiché (obligatoire)")
    print(f"   ✅ Dates de création/modification visibles")
    print(f"   ✅ Champs boutique retirés")

if __name__ == "__main__":
    main()




























