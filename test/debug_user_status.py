#!/usr/bin/env python3
"""
Script de debug pour vérifier l'état des utilisateurs
"""

import os
import django
import sys

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Entreprise, Boutique

User = get_user_model()

def debug_user_status():
    """Debug l'état des utilisateurs créés"""
    print("🔍 DEBUG - État des utilisateurs")
    print("=" * 50)
    
    # Lister tous les utilisateurs
    users = User.objects.all()
    print(f"👥 Total utilisateurs: {users.count()}")
    
    for user in users:
        print(f"\n👤 Utilisateur: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Rôle: {user.role}")
        print(f"   Actif: {user.is_active}")
        print(f"   Entreprise: {user.entreprise.nom if user.entreprise else 'Aucune'}")
        print(f"   Boutique: {user.boutique.nom if user.boutique else 'Aucune'}")
        print(f"   Créé: {user.created_at}")
    
    # Lister toutes les entreprises
    entreprises = Entreprise.objects.all()
    print(f"\n🏢 Total entreprises: {entreprises.count()}")
    
    for entreprise in entreprises:
        print(f"\n🏢 Entreprise: {entreprise.nom}")
        print(f"   ID: {entreprise.id_entreprise}")
        print(f"   Email: {entreprise.email}")
        print(f"   Pack: {entreprise.pack_type}")
        print(f"   Créée: {entreprise.created_at}")
        
        # Utilisateurs de cette entreprise
        users_entreprise = entreprise.users.all()
        print(f"   Utilisateurs: {users_entreprise.count()}")
        for user in users_entreprise:
            print(f"     - {user.username} ({user.role})")
        
        # Boutiques de cette entreprise
        boutiques = entreprise.boutiques.all()
        print(f"   Boutiques: {boutiques.count()}")
        for boutique in boutiques:
            print(f"     - {boutique.nom}")
    
    # Lister toutes les boutiques
    boutiques = Boutique.objects.all()
    print(f"\n🏪 Total boutiques: {boutiques.count()}")
    
    for boutique in boutiques:
        print(f"\n🏪 Boutique: {boutique.nom}")
        print(f"   Entreprise: {boutique.entreprise.nom if boutique.entreprise else 'Aucune'}")
        print(f"   Responsable: {boutique.responsable}")
        print(f"   Créée: {boutique.created_at}")

if __name__ == "__main__":
    debug_user_status()
