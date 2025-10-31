"""
Test complet du système de tarification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import SubscriptionPlan, EntrepriseSubscription, Entreprise
from django.utils import timezone
from datetime import timedelta

def test_plans():
    """Test la création et l'affichage des plans"""
    print("\n" + "="*60)
    print("TEST 1: Vérification des Plans")
    print("="*60)
    
    plans = SubscriptionPlan.objects.all()
    print(f"\n✅ {plans.count()} plans trouvés:")
    
    for plan in plans:
        print(f"\n  {plan.display_name} ({plan.name})")
        print(f"    Prix: {plan.price_monthly} XAF/mois")
        print(f"    Boutiques: {plan.max_boutiques}")
        print(f"    Users: {plan.max_users}")
        print(f"    Produits: {plan.max_produits}")
        print(f"    Inventaires: {'✅' if plan.allow_inventory else '❌'}")
        print(f"    Codes-barres: {'✅' if plan.allow_barcode_generation else '❌'}")
        print(f"    Partenaires: {'✅' if plan.allow_partners else '❌'}")
    
    return True

def test_subscription_creation():
    """Test la création d'un abonnement"""
    print("\n" + "="*60)
    print("TEST 2: Création d'un Abonnement")
    print("="*60)
    
    entreprise = Entreprise.objects.first()
    if not entreprise:
        print("❌ Aucune entreprise trouvée")
        return False
    
    print(f"  Entreprise: {entreprise.nom}")
    
    free_plan = SubscriptionPlan.objects.get(name='free')
    print(f"  Plan: {free_plan.display_name}")
    
    subscription, created = EntrepriseSubscription.objects.update_or_create(
        entreprise=entreprise,
        defaults={
            'plan': free_plan,
            'start_date': timezone.now(),
            'end_date': timezone.now() + timedelta(days=90),
            'billing_period': 'monthly',
            'status': 'active'
        }
    )
    
    print(f"  {'✅ Abonnement créé' if created else '🔄 Abonnement mis à jour'}")
    print(f"  Date début: {subscription.start_date.strftime('%Y-%m-%d')}")
    print(f"  Date fin: {subscription.end_date.strftime('%Y-%m-%d')}")
    print(f"  Jours restants: {subscription.get_days_until_expiry()}")
    
    return True

def test_extend_subscription():
    """Test le renouvellement"""
    print("\n" + "="*60)
    print("TEST 3: Renouvellement de l'Abonnement")
    print("="*60)
    
    entreprise = Entreprise.objects.first()
    if not entreprise:
        return False
    
    subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
    if not subscription:
        return False
    
    print(f"  Date de fin actuelle: {subscription.end_date.strftime('%Y-%m-%d')}")
    
    new_end_date = subscription.extend_subscription(30)
    
    print(f"  ✅ Abonnement prolongé")
    print(f"  Nouvelle date de fin: {new_end_date.strftime('%Y-%m-%d')}")
    print(f"  Jours restants: {subscription.get_days_until_expiry()}")
    
    return True

def test_get_price():
    """Test le calcul du prix"""
    print("\n" + "="*60)
    print("TEST 4: Calcul du Prix")
    print("="*60)
    
    entreprise = Entreprise.objects.first()
    if not entreprise:
        return False
    
    subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
    if not subscription:
        return False
    
    subscription.billing_period = 'monthly'
    prix_mensuel = subscription.get_price()
    print(f"  Période: Mensuel")
    print(f"  Prix: {prix_mensuel} XAF")
    
    subscription.billing_period = 'yearly'
    prix_annuel = subscription.get_price()
    print(f"  Période: Annuel")
    print(f"  Prix: {prix_annuel} XAF")
    
    return True

def run_all_tests():
    """Exécuter tous les tests"""
    print("\n🧪 TESTS COMPLETS DU SYSTÈME DE TARIFICATION")
    print("=" * 60)
    
    tests = [test_plans, test_subscription_creation, test_extend_subscription, test_get_price]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("RÉSUMÉ: " + f"{sum(results)}/{len(results)} tests réussis")
    print("="*60)
    
    return all(results)

if __name__ == '__main__':
    run_all_tests()







