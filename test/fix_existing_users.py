#!/usr/bin/env python3
"""
Script pour corriger les utilisateurs existants
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

def fix_existing_users():
    """Corriger les utilisateurs existants"""
    print("🔧 Correction des utilisateurs existants")
    print("=" * 50)
    
    # Récupérer toutes les entreprises
    entreprises = Entreprise.objects.all()
    
    for entreprise in entreprises:
        print(f"\n🏢 Entreprise: {entreprise.nom}")
        
        # Chercher les utilisateurs qui correspondent à cette entreprise
        # par email ou par nom
        users_to_fix = User.objects.filter(
            email__icontains=entreprise.nom.lower().replace(' ', '.')
        ).exclude(entreprise=entreprise)
        
        if not users_to_fix.exists():
            # Essayer de trouver par email similaire
            entreprise_email_prefix = entreprise.email.split('@')[0]
            users_to_fix = User.objects.filter(
                email__icontains=entreprise_email_prefix
            ).exclude(entreprise=entreprise)
        
        if users_to_fix.exists():
            print(f"   👥 Utilisateurs à corriger: {users_to_fix.count()}")
            
            # Récupérer la boutique par défaut de l'entreprise
            boutique_default = entreprise.boutiques.first()
            
            for user in users_to_fix:
                print(f"     🔧 Correction: {user.username}")
                user.entreprise = entreprise
                if boutique_default:
                    user.boutique = boutique_default
                user.save()
                print(f"       ✅ Entreprise: {entreprise.nom}")
                if boutique_default:
                    print(f"       ✅ Boutique: {boutique_default.nom}")
        else:
            print("   ℹ️  Aucun utilisateur à corriger")
    
    # Vérifier les résultats
    print("\n📊 Vérification des corrections:")
    users_with_entreprise = User.objects.filter(entreprise__isnull=False)
    print(f"👥 Utilisateurs avec entreprise: {users_with_entreprise.count()}")
    
    for user in users_with_entreprise:
        print(f"   - {user.username}: {user.entreprise.nom}")

if __name__ == "__main__":
    fix_existing_users()
