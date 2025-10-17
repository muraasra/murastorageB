#!/usr/bin/env python3
"""
Créer un utilisateur de test pour les tests
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Entreprise, Boutique

User = get_user_model()

def create_test_data():
    """Créer des données de test"""
    print("🔧 Création des données de test...")
    
    # 1. Créer une entreprise de test
    entreprise, created = Entreprise.objects.get_or_create(
        nom="Entreprise Test",
        defaults={
            'secteur_activite': 'technologie',
            'ville': 'Douala',
            'pack_type': 'professional',
            'nombre_employes': 10,
            'annee_creation': 2020,
            'site_web': 'https://test.com'
        }
    )
    
    if created:
        print(f"   ✅ Entreprise créée: {entreprise.nom} (ID: {entreprise.id_entreprise})")
    else:
        print(f"   ℹ️  Entreprise existante: {entreprise.nom} (ID: {entreprise.id_entreprise})")
    
    # 2. Créer un entrepôt de test
    boutique, created = Boutique.objects.get_or_create(
        nom="Entrepôt Test",
        defaults={
            'entreprise': entreprise,
            'ville': 'Douala',
            'responsable': 'Responsable Test',
            'adresse': 'Adresse test, Douala',
            'telephone': '+237 6XX XXX XXX'
        }
    )
    
    if created:
        print(f"   ✅ Entrepôt créé: {boutique.nom} (ID: {boutique.id})")
    else:
        print(f"   ℹ️  Entrepôt existant: {boutique.nom} (ID: {boutique.id})")
    
    # 3. Créer un utilisateur SuperAdmin de test
    user, created = User.objects.get_or_create(
        email="admin@test.com",
        defaults={
            'username': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'Test',
            'role': 'superadmin',
            'entreprise': entreprise,
            'boutique': boutique,
            'telephone': '+237 6XX XXX XXX',
            'poste': 'Super Administrateur',
            'is_active_employee': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"   ✅ Utilisateur SuperAdmin créé: {user.first_name} {user.last_name}")
        print(f"   📧 Email: {user.email}")
        print(f"   🔑 Mot de passe: admin123")
    else:
        print(f"   ℹ️  Utilisateur SuperAdmin existant: {user.first_name} {user.last_name}")
        # Mettre à jour le mot de passe au cas où
        user.set_password('admin123')
        user.save()
        print(f"   🔑 Mot de passe mis à jour: admin123")
    
    # 4. Créer un utilisateur normal de test
    user_normal, created = User.objects.get_or_create(
        email="user@test.com",
        defaults={
            'username': 'user@test.com',
            'first_name': 'User',
            'last_name': 'Test',
            'role': 'user',
            'entreprise': entreprise,
            'boutique': boutique,
            'telephone': '+237 6XX XXX XXX',
            'poste': 'Gestionnaire de stock',
            'is_active_employee': True
        }
    )
    
    if created:
        user_normal.set_password('user123')
        user_normal.save()
        print(f"   ✅ Utilisateur normal créé: {user_normal.first_name} {user_normal.last_name}")
        print(f"   📧 Email: {user_normal.email}")
        print(f"   🔑 Mot de passe: user123")
    else:
        print(f"   ℹ️  Utilisateur normal existant: {user_normal.first_name} {user_normal.last_name}")
        # Mettre à jour le mot de passe au cas où
        user_normal.set_password('user123')
        user_normal.save()
        print(f"   🔑 Mot de passe mis à jour: user123")
    
    print("\n✅ Données de test créées avec succès!")
    print("\n📋 Informations de connexion:")
    print(f"   SuperAdmin: admin@test.com / admin123")
    print(f"   Utilisateur: user@test.com / user123")
    print(f"   ID Entreprise: {entreprise.id_entreprise}")

if __name__ == "__main__":
    create_test_data()
