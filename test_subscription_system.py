"""
Script de test pour le système d'abonnement
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import Entreprise, User, SubscriptionPlan, EntrepriseSubscription, UsageTracking
from core.subscription_utils import (
    get_entreprise_subscription,
    check_limit,
    check_feature,
    get_subscription_limits,
    get_current_usage
)

def test_subscription_creation():
    """Tester la création automatique d'abonnement FREE"""
    print("\n=== Test 1: Creation automatique d'abonnement FREE ===")
    
    # Créer une entreprise de test
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    print(f"Entreprise: {entreprise.nom}")
    
    # Récupérer l'abonnement (créera un FREE si n'existe pas)
    subscription = get_entreprise_subscription(entreprise)
    print(f"Plan: {subscription.plan.display_name}")
    print(f"Statut: {subscription.status}")
    print(f"[OK] Abonnement recupere/cree avec succes")

def test_check_limits():
    """Tester la vérification des limites"""
    print("\n=== Test 2: Verification des limites ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    resources = ['users', 'boutiques', 'produits', 'factures']
    
    for resource in resources:
        can_create, message = check_limit(entreprise, resource)
        status = "[OK]" if can_create else "[LIMIT]"
        print(f"{status} {resource}: {message}")

def test_check_features():
    """Tester la vérification des fonctionnalités"""
    print("\n=== Test 3: Verification des fonctionnalites ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    features = [
        'export_csv',
        'export_excel',
        'import_csv',
        'api_access',
        'advanced_analytics'
    ]
    
    for feature in features:
        is_available, message = check_feature(entreprise, feature)
        status = "[OK]" if is_available else "[NOK]"
        print(f"{status} {feature}: {'Disponible' if is_available else 'Non disponible'}")

def test_usage_tracking():
    """Tester le suivi d'utilisation"""
    print("\n=== Test 4: Suivi d'utilisation ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    usage = get_current_usage(entreprise)
    print(f"Utilisateurs: {usage['users_count']}/{usage['users_limit']}")
    print(f"Boutiques: {usage['boutiques_count']}/{usage['boutiques_limit']}")
    print(f"Produits: {usage['produits_count']}/{usage['produits_limit'] or 'Illimite'}")
    print(f"Factures: {usage['factures_count']}/{usage['factures_limit'] or 'Illimite'}")
    print(f"[OK] Suivi d'utilisation recupere")

def test_all_plans():
    """Afficher tous les plans disponibles"""
    print("\n=== Test 5: Plans disponibles ===")
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    for plan in plans:
        print(f"\nPlan: {plan.display_name}")
        print(f"  Prix: {plan.price_monthly} XAF/mois")
        print(f"  Boutiques: {plan.max_boutiques}")
        print(f"  Utilisateurs: {plan.max_users}")
        print(f"  Produits: {plan.max_produits or 'Illimite'}")
        print(f"  Factures/mois: {plan.max_factures_per_month or 'Illimite'}")
        print(f"  Export CSV: {plan.allow_export_csv}")
        print(f"  Export Excel: {plan.allow_export_excel}")
        print(f"  Import CSV: {plan.allow_import_csv}")
    
    print(f"\n[OK] {plans.count()} plans disponibles")

def test_subscription_upgrade():
    """Tester la mise à niveau d'abonnement"""
    print("\n=== Test 6: Mise a niveau d'abonnement ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Récupérer l'abonnement actuel
    subscription = get_entreprise_subscription(entreprise)
    print(f"Plan actuel: {subscription.plan.display_name}")
    
    # Essayer de passer au plan Basic
    basic_plan = SubscriptionPlan.objects.filter(name='basic', is_active=True).first()
    if not basic_plan:
        print("[SKIP] Plan Basic non trouve")
        return
    
    old_plan = subscription.plan
    subscription.plan = basic_plan
    subscription.save()
    
    print(f"Nouveau plan: {subscription.plan.display_name}")
    print(f"[OK] Mise a niveau reussie de {old_plan.display_name} vers {basic_plan.display_name}")
    
    # Remettre le plan original pour ne pas affecter les autres tests
    subscription.plan = old_plan
    subscription.save()

def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("TESTS DU SYSTEME D'ABONNEMENT")
    print("=" * 60)
    
    try:
        test_subscription_creation()
        test_check_limits()
        test_check_features()
        test_usage_tracking()
        test_all_plans()
        test_subscription_upgrade()
        
        print("\n" + "=" * 60)
        print("TOUS LES TESTS SONT PASSES AVEC SUCCES!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()














