#!/usr/bin/env python3
"""
Script pour associer manuellement les utilisateurs aux entreprises
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

def manual_fix_users():
    """Association manuelle des utilisateurs aux entreprises"""
    print("🔧 Association manuelle des utilisateurs")
    print("=" * 50)
    
    # Récupérer les entreprises récentes
    entreprises = Entreprise.objects.all().order_by('-created_at')[:3]
    
    # Récupérer les utilisateurs récents sans entreprise
    users_without_entreprise = User.objects.filter(
        entreprise__isnull=True,
        role='superadmin'
    ).order_by('-created_at')[:3]
    
    print(f"🏢 Entreprises disponibles: {entreprises.count()}")
    for entreprise in entreprises:
        print(f"   - {entreprise.nom} (ID: {entreprise.id_entreprise})")
    
    print(f"\n👥 Utilisateurs sans entreprise: {users_without_entreprise.count()}")
    for user in users_without_entreprise:
        print(f"   - {user.username} ({user.email})")
    
    # Association manuelle
    associations = [
        ("debug.test.1759282339@example.com", "Entreprise Debug 1759282339"),
        ("test.api.1759282349@example.com", "Entreprise Test 1759282349"),
        ("test.auth.1759282399@example.com", "Entreprise Auth 1759282399"),
    ]
    
    print(f"\n🔗 Associations:")
    for email, entreprise_nom in associations:
        try:
            user = User.objects.get(email=email)
            entreprise = Entreprise.objects.get(nom=entreprise_nom)
            boutique_default = entreprise.boutiques.first()
            
            user.entreprise = entreprise
            if boutique_default:
                user.boutique = boutique_default
            
            user.save()
            
            print(f"   ✅ {user.username} → {entreprise.nom}")
            if boutique_default:
                print(f"      🏪 Boutique: {boutique_default.nom}")
                
        except User.DoesNotExist:
            print(f"   ❌ Utilisateur non trouvé: {email}")
        except Entreprise.DoesNotExist:
            print(f"   ❌ Entreprise non trouvée: {entreprise_nom}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Vérification finale
    print(f"\n📊 Vérification finale:")
    users_with_entreprise = User.objects.filter(entreprise__isnull=False)
    print(f"👥 Utilisateurs avec entreprise: {users_with_entreprise.count()}")
    
    for user in users_with_entreprise:
        print(f"   - {user.username}: {user.entreprise.nom}")

if __name__ == "__main__":
    manual_fix_users()
