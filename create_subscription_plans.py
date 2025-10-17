"""
Script pour initialiser les plans d'abonnement dans la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import SubscriptionPlan

def create_plans():
    """Créer les plans d'abonnement"""
    
    plans_data = [
        {
            'name': 'free',
            'display_name': 'Free',
            'description': 'Plan gratuit avec limitations - Idéal pour débuter',
            'price_monthly': 0,
            'price_yearly': 0,
            'max_entreprises': 1,
            'max_boutiques': 1,
            'max_users': 2,
            'max_produits': 50,
            'max_factures_per_month': 100,
            'allow_export_csv': False,
            'allow_export_excel': False,
            'allow_import_csv': False,
            'allow_api_access': False,
            'allow_multiple_entreprises': False,
            'allow_advanced_analytics': False,
            'allow_custom_branding': False,
            'support_level': 'email',
            'is_active': True,
        },
        {
            'name': 'basic',
            'display_name': 'Basic',
            'description': 'Plan de base pour petites entreprises',
            'price_monthly': 15000,  # 15 000 XAF/mois
            'price_yearly': 150000,  # 150 000 XAF/an (2 mois gratuits)
            'max_entreprises': 1,
            'max_boutiques': 3,
            'max_users': 5,
            'max_produits': 500,
            'max_factures_per_month': 1000,
            'allow_export_csv': True,
            'allow_export_excel': False,
            'allow_import_csv': False,
            'allow_api_access': False,
            'allow_multiple_entreprises': False,
            'allow_advanced_analytics': False,
            'allow_custom_branding': False,
            'support_level': 'email',
            'is_active': True,
        },
        {
            'name': 'premium',
            'display_name': 'Premium',
            'description': 'Plan avancé pour entreprises en croissance',
            'price_monthly': 35000,  # 35 000 XAF/mois
            'price_yearly': 350000,  # 350 000 XAF/an (2 mois gratuits)
            'max_entreprises': 1,
            'max_boutiques': 10,
            'max_users': 25,
            'max_produits': None,  # Illimité
            'max_factures_per_month': None,  # Illimité
            'allow_export_csv': True,
            'allow_export_excel': True,
            'allow_import_csv': True,
            'allow_api_access': False,
            'allow_multiple_entreprises': False,
            'allow_advanced_analytics': True,
            'allow_custom_branding': True,
            'support_level': 'priority',
            'is_active': True,
        },
        {
            'name': 'organisation',
            'display_name': 'Organisation',
            'description': 'Plan entreprise avec toutes les fonctionnalités',
            'price_monthly': 75000,  # 75 000 XAF/mois
            'price_yearly': 750000,  # 750 000 XAF/an (2 mois gratuits)
            'max_entreprises': 999999,  # Illimité (grand nombre)
            'max_boutiques': 999999,  # Illimité (grand nombre)
            'max_users': 999999,  # Illimité (grand nombre)
            'max_produits': None,  # Illimité
            'max_factures_per_month': None,  # Illimité
            'allow_export_csv': True,
            'allow_export_excel': True,
            'allow_import_csv': True,
            'allow_api_access': True,
            'allow_multiple_entreprises': True,
            'allow_advanced_analytics': True,
            'allow_custom_branding': True,
            'support_level': 'dedicated',
            'is_active': True,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.update_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        
        if created:
            print(f"[+] Plan cree: {plan.display_name}")
            created_count += 1
        else:
            print(f"[*] Plan mis a jour: {plan.display_name}")
            updated_count += 1
    
    print(f"\nResume:")
    print(f"   - Plans crees: {created_count}")
    print(f"   - Plans mis a jour: {updated_count}")
    print(f"   - Total: {created_count + updated_count}")
    
    # Afficher tous les plans
    print(f"\nPlans disponibles:")
    for plan in SubscriptionPlan.objects.all().order_by('price_monthly'):
        print(f"   - {plan.display_name}: {plan.price_monthly} XAF/mois")
        print(f"     * Max boutiques: {plan.max_boutiques or 'Illimité'}")
        print(f"     * Max utilisateurs: {plan.max_users or 'Illimité'}")
        print(f"     * Max produits: {plan.max_produits or 'Illimité'}")
        print(f"     * Max factures/mois: {plan.max_factures_per_month or 'Illimité'}")
        print()

if __name__ == '__main__':
    print("Initialisation des plans d'abonnement...\n")
    create_plans()
    print("\nTermine!")

