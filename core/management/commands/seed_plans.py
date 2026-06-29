"""
Commande pour initialiser/mettre à jour les plans d'abonnement MuraStorage.
Usage: python manage.py seed_plans
"""
from django.core.management.base import BaseCommand
from core.models import SubscriptionPlan


PLANS = [
    {
        'name': 'free',
        'display_name': 'Essai Gratuit',
        'description': 'Découvrez MuraStorage pendant 3 mois — sans carte bancaire.',
        'price_monthly': 0,
        'price_yearly': 0,
        'max_boutiques': 1,
        'max_users': 3,
        'max_produits': 30,
        'max_factures_per_month': 30,
        'max_inventaires_per_month': 0,
        'max_transfers_per_month': 0,
        'allow_inventory': False,
        'allow_transfers': False,
        'allow_barcode_generation': False,
        'allow_partners': True,
        'allow_export_csv': False,
        'allow_export_excel': False,
        'allow_import_csv': False,
        'allow_api_access': False,
        'allow_multiple_entreprises': False,
        'allow_advanced_analytics': False,
        'allow_custom_branding': False,
        'alert_level': 'none',
        'support_level': 'email',
        'is_active': True,
    },
    {
        'name': 'starter',
        'display_name': 'Starter',
        'description': 'Pour les petits commerces qui démarrent leur gestion de stock.',
        'price_monthly': 4900,
        'price_yearly': 52920,  # -10%
        'max_boutiques': 2,
        'max_users': 5,
        'max_produits': 200,
        'max_factures_per_month': 200,
        'max_inventaires_per_month': 1,
        'max_transfers_per_month': 0,
        'allow_inventory': True,
        'allow_transfers': False,
        'allow_barcode_generation': False,
        'allow_partners': True,
        'allow_export_csv': True,
        'allow_export_excel': False,
        'allow_import_csv': False,
        'allow_api_access': False,
        'allow_multiple_entreprises': False,
        'allow_advanced_analytics': False,
        'allow_custom_branding': False,
        'alert_level': 'simple',
        'support_level': 'email',
        'is_active': True,
    },
    {
        'name': 'business',
        'display_name': 'Business',
        'description': 'Pour les PME avec plusieurs entrepôts et une équipe structurée.',
        'price_monthly': 9900,
        'price_yearly': 106920,  # -10%
        'max_boutiques': 3,
        'max_users': 15,
        'max_produits': 1000,
        'max_factures_per_month': None,  # illimité
        'max_inventaires_per_month': 5,
        'max_transfers_per_month': 100,
        'allow_inventory': True,
        'allow_transfers': True,
        'allow_barcode_generation': True,
        'allow_partners': True,
        'allow_export_csv': True,
        'allow_export_excel': True,
        'allow_import_csv': True,
        'allow_api_access': False,
        'allow_multiple_entreprises': False,
        'allow_advanced_analytics': True,
        'allow_custom_branding': False,
        'alert_level': 'advanced',
        'support_level': 'priority',
        'is_active': True,
    },
    {
        'name': 'pro',
        'display_name': 'Pro',
        'description': 'Toutes les fonctionnalités sans aucune limite. Pour les entreprises ambitieuses.',
        'price_monthly': 19900,
        'price_yearly': 214920,  # -10%
        'max_boutiques': 10,
        'max_users': 50,
        'max_produits': None,   # illimité
        'max_factures_per_month': None,  # illimité
        'max_inventaires_per_month': None,
        'max_transfers_per_month': None,
        'allow_inventory': True,
        'allow_transfers': True,
        'allow_barcode_generation': True,
        'allow_partners': True,
        'allow_export_csv': True,
        'allow_export_excel': True,
        'allow_import_csv': True,
        'allow_api_access': True,
        'allow_multiple_entreprises': False,
        'allow_advanced_analytics': True,
        'allow_custom_branding': True,
        'alert_level': 'multi_warehouse',
        'support_level': 'dedicated',
        'is_active': True,
    },
]


class Command(BaseCommand):
    help = 'Initialise ou met à jour les plans d\'abonnement MuraStorage'

    def handle(self, *args, **options):
        for plan_data in PLANS:
            name = plan_data['name']
            obj, created = SubscriptionPlan.objects.update_or_create(
                name=name,
                defaults=plan_data,
            )
            action = 'Créé' if created else 'Mis à jour'
            self.stdout.write(self.style.SUCCESS(
                f'{action}: {obj.display_name} ({obj.price_monthly} FCFA/mois)'
            ))

        # Désactiver les anciens plans qui ne sont plus dans la liste
        valid_names = [p['name'] for p in PLANS]
        old_plans = SubscriptionPlan.objects.exclude(name__in=valid_names)
        if old_plans.exists():
            names = list(old_plans.values_list('name', flat=True))
            old_plans.update(is_active=False)
            self.stdout.write(self.style.WARNING(f'Désactivés (obsolètes): {names}'))

        self.stdout.write(self.style.SUCCESS('\nOK - Plans d\'abonnement synchronises avec succes.'))
