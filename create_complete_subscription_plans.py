"""
Script pour créer les 4 plans d'abonnement complets
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import SubscriptionPlan, EntrepriseSubscription, Entreprise
from django.utils import timezone
from datetime import timedelta

def create_plans():
    """Créer les 4 plans d'abonnement"""
    
    # Plan FREE
    free_plan, created = SubscriptionPlan.objects.update_or_create(
        name='free',
        defaults={
            'display_name': 'Free',
            'description': 'Essai gratuit de 3 mois',
            'price_monthly': 0,
            'price_yearly': 0,
            'max_entreprises': 1,
            'max_boutiques': 1,
            'max_users': 2,
            'max_produits': 15,
            'max_factures_per_month': 100,
            'max_inventaires_per_month': 0,
            'max_transfers_per_month': 0,
            'allow_inventory': False,
            'allow_transfers': False,
            'allow_barcode_generation': False,
            'allow_partners': False,
            'allow_export_csv': False,
            'allow_export_excel': False,
            'allow_import_csv': False,
            'allow_api_access': False,
            'alert_level': 'none',
            'support_level': 'email',
            'is_active': True,
        }
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} plan FREE")
    
    # Plan BASIC
    basic_plan, created = SubscriptionPlan.objects.update_or_create(
        name='basic',
        defaults={
            'display_name': 'Basic',
            'description': 'Idéal pour les petites entreprises',
            'price_monthly': 9900,
            'price_yearly': 118800,  # 9900 * 12
            'max_entreprises': 1,
            'max_boutiques': 2,
            'max_users': 3,
            'max_produits': 100,
            'max_factures_per_month': 500,
            'max_inventaires_per_month': 0,
            'max_transfers_per_month': 25,
            'allow_inventory': False,
            'allow_transfers': True,
            'allow_barcode_generation': True,
            'allow_partners': True,
            'allow_export_csv': True,
            'allow_export_excel': True,
            'allow_import_csv': True,
            'allow_api_access': False,
            'alert_level': 'simple',
            'support_level': 'email',
            'is_active': True,
        }
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} plan BASIC")
    
    # Plan PREMIUM
    premium_plan, created = SubscriptionPlan.objects.update_or_create(
        name='premium',
        defaults={
            'display_name': 'Premium',
            'description': 'Pour les entreprises en croissance',
            'price_monthly': 29000,
            'price_yearly': 348000,  # 29000 * 12
            'max_entreprises': 1,
            'max_boutiques': 5,
            'max_users': 10,
            'max_produits': 500,
            'max_factures_per_month': 2000,
            'max_inventaires_per_month': 1,
            'max_transfers_per_month': 100,
            'allow_inventory': True,
            'allow_transfers': True,
            'allow_barcode_generation': True,
            'allow_partners': True,
            'allow_export_csv': True,
            'allow_export_excel': True,
            'allow_import_csv': True,
            'allow_api_access': False,
            'alert_level': 'advanced',
            'support_level': 'priority',
            'is_active': True,
        }
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} plan PREMIUM")
    
    # Plan ORGANISATION
    org_plan, created = SubscriptionPlan.objects.update_or_create(
        name='organisation',
        defaults={
            'display_name': 'Organisation',
            'description': 'Solution personnalisable illimitée',
            'price_monthly': 55000,
            'price_yearly': 660000,  # 55000 * 12
            'max_entreprises': 999999,  # Illimité
            'max_boutiques': 999999,  # Illimité
            'max_users': 999999,  # Illimité
            'max_produits': 999999,  # Illimité
            'max_factures_per_month': 999999,  # Illimité
            'max_inventaires_per_month': 999999,  # Illimité
            'max_transfers_per_month': 999999,  # Illimité
            'allow_inventory': True,
            'allow_transfers': True,
            'allow_barcode_generation': True,
            'allow_partners': True,
            'allow_export_csv': True,
            'allow_export_excel': True,
            'allow_import_csv': True,
            'allow_api_access': True,
            'alert_level': 'multi_warehouse',
            'support_level': 'dedicated',
            'is_active': True,
        }
    )
    print(f"{'✅ Créé' if created else '🔄 Mis à jour'} plan ORGANISATION")
    
    print("\n✅ Tous les plans ont été créés/mis à jour avec succès!")

if __name__ == '__main__':
    create_plans()

