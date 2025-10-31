"""Script pour vérifier les plans créés"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import SubscriptionPlan

print("📋 Plans d'abonnement créés:")
print("=" * 60)

for plan in SubscriptionPlan.objects.all().order_by('price_monthly'):
    print(f"\n{plan.display_name} ({plan.name})")
    print(f"  Prix: {plan.price_monthly} XAF/mois")
    print(f"  Boutiques: {plan.max_boutiques}")
    print(f"  Utilisateurs: {plan.max_users}")
    print(f"  Produits: {plan.max_produits}")
    print(f"  Factures/mois: {plan.max_factures_per_month}")
    print(f"  Inventaires: {'✅' if plan.allow_inventory else '❌'}")
    print(f"  Transferts: {'✅' if plan.allow_transfers else '❌'}")
    print(f"  Codes-barres: {'✅' if plan.allow_barcode_generation else '❌'}")
    print(f"  Partenaires: {'✅' if plan.allow_partners else '❌'}")

print("\n✅ Vérification terminée!")







