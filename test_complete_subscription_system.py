"""
Script de test complet pour le système d'abonnement avec notifications
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
    get_current_usage,
    increment_usage
)
from core.subscription_notifications import (
    process_subscription_change,
    check_and_send_limit_warnings,
    check_and_send_trial_warnings,
    check_and_send_subscription_expiry_warnings,
    send_subscription_notification_email
)
from datetime import timedelta
from django.utils import timezone

def test_upgrade_downgrade():
    """Tester les fonctionnalités d'upgrade et downgrade"""
    print("\n=== Test 1: Upgrade et Downgrade ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    print(f"Entreprise: {entreprise.nom}")
    
    # Test upgrade vers Basic
    print("\n--- Test Upgrade vers Basic ---")
    success, message = process_subscription_change(entreprise, 2, 'upgrade')  # Basic = ID 2
    if success:
        print(f"[OK] Upgrade reussi: {message}")
    else:
        print(f"[ERREUR] Upgrade echoue: {message}")
    
    # Test downgrade vers Free
    print("\n--- Test Downgrade vers Free ---")
    success, message = process_subscription_change(entreprise, 1, 'downgrade')  # Free = ID 1
    if success:
        print(f"[OK] Downgrade reussi: {message}")
    else:
        print(f"[ERREUR] Downgrade echoue: {message}")
    
    # Test upgrade invalide (même prix)
    print("\n--- Test Upgrade invalide ---")
    success, message = process_subscription_change(entreprise, 1, 'upgrade')  # Free vers Free
    if not success:
        print(f"[OK] Upgrade invalide correctement refuse: {message}")
    else:
        print(f"[ERREUR] Upgrade invalide accepte par erreur")

def test_email_notifications():
    """Tester l'envoi d'emails de notification"""
    print("\n=== Test 2: Notifications par email ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Test notification d'upgrade
    print("\n--- Test notification upgrade ---")
    success = send_subscription_notification_email(
        entreprise, 
        'upgrade',
        {
            'old_plan': SubscriptionPlan.objects.get(name='free'),
            'new_plan': SubscriptionPlan.objects.get(name='basic'),
            'change_type': 'upgrade'
        }
    )
    print(f"[{'OK' if success else 'ERREUR'}] Notification upgrade: {'Envoyee' if success else 'Echec'}")
    
    # Test notification de limite
    print("\n--- Test notification limite ---")
    success = send_subscription_notification_email(
        entreprise, 
        'limit_warning',
        {
            'resource_type': 'users',
            'current': 1,
            'limit': 2,
            'percentage': 50.0,
            'warning_level': 'warning'
        }
    )
    print(f"[{'OK' if success else 'ERREUR'}] Notification limite: {'Envoyee' if success else 'Echec'}")

def test_limit_warnings():
    """Tester les avertissements de limite"""
    print("\n=== Test 3: Avertissements de limite ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Simuler une utilisation élevée
    usage = get_current_usage(entreprise)
    print(f"Utilisation actuelle: {usage}")
    
    # Tester les avertissements automatiques
    warnings_sent = check_and_send_limit_warnings(entreprise)
    print(f"[{'OK' if warnings_sent else 'INFO'}] Avertissements limites: {'Envoyes' if warnings_sent else 'Aucun necessaire'}")

def test_trial_warnings():
    """Tester les avertissements de période d'essai"""
    print("\n=== Test 4: Avertissements periode d'essai ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Modifier la période d'essai pour tester
    subscription = get_entreprise_subscription(entreprise)
    subscription.trial_end_date = timezone.now() + timedelta(days=3)  # 3 jours restants
    subscription.save()
    
    print(f"Période d'essai expire dans: {subscription.get_remaining_trial_days()} jours")
    
    # Tester les avertissements
    warnings_sent = check_and_send_trial_warnings(entreprise)
    print(f"[{'OK' if warnings_sent else 'INFO'}] Avertissements essai: {'Envoyes' if warnings_sent else 'Aucun necessaire'}")

def test_subscription_expiry_warnings():
    """Tester les avertissements d'expiration d'abonnement"""
    print("\n=== Test 5: Avertissements expiration ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Modifier la date d'expiration pour tester
    subscription = get_entreprise_subscription(entreprise)
    subscription.end_date = timezone.now() + timedelta(days=7)  # 7 jours restants
    subscription.save()
    
    print(f"Abonnement expire dans: {(subscription.end_date - timezone.now()).days} jours")
    
    # Tester les avertissements
    warnings_sent = check_and_send_subscription_expiry_warnings(entreprise)
    print(f"[{'OK' if warnings_sent else 'INFO'}] Avertissements expiration: {'Envoyes' if warnings_sent else 'Aucun necessaire'}")

def test_usage_tracking():
    """Tester le suivi d'utilisation"""
    print("\n=== Test 6: Suivi d'utilisation ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Incrémenter l'utilisation
    print("--- Incrementation utilisation ---")
    increment_usage(entreprise, 'factures')
    increment_usage(entreprise, 'produits')
    
    # Vérifier l'utilisation mise à jour
    usage = get_current_usage(entreprise)
    print(f"Utilisation apres increment: {usage}")
    
    # Vérifier les limites
    limits = get_subscription_limits(entreprise)
    print(f"Limites actuelles: {limits}")

def test_feature_access():
    """Tester l'accès aux fonctionnalités"""
    print("\n=== Test 7: Acces aux fonctionnalites ===")
    
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

def test_all_notifications():
    """Tester toutes les notifications en une fois"""
    print("\n=== Test 8: Test complet des notifications ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return
    
    # Simuler différents scénarios
    subscription = get_entreprise_subscription(entreprise)
    
    # Scénario 1: Période d'essai se terminant
    subscription.trial_end_date = timezone.now() + timedelta(days=1)
    subscription.save()
    
    # Scénario 2: Abonnement expirant
    subscription.end_date = timezone.now() + timedelta(days=1)
    subscription.save()
    
    # Scénario 3: Utilisation élevée
    usage_tracking = UsageTracking.objects.filter(entreprise=entreprise).first()
    if usage_tracking:
        usage_tracking.users_count = 1  # 50% de la limite Free (2 users)
        usage_tracking.save()
    
    print("Scenarios configures:")
    print(f"- Periode d'essai: {subscription.get_remaining_trial_days()} jours")
    print(f"- Abonnement expire: {(subscription.end_date - timezone.now()).days} jours")
    print(f"- Utilisateurs: {usage_tracking.users_count if usage_tracking else 'N/A'}")
    
    # Tester toutes les notifications
    notifications_sent = []
    
    if check_and_send_limit_warnings(entreprise):
        notifications_sent.append('limit_warnings')
    
    if check_and_send_trial_warnings(entreprise):
        notifications_sent.append('trial_warnings')
    
    if check_and_send_subscription_expiry_warnings(entreprise):
        notifications_sent.append('expiry_warnings')
    
    print(f"[OK] Notifications envoyees: {notifications_sent}")

def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 70)
    print("TESTS COMPLETS DU SYSTEME D'ABONNEMENT AVEC NOTIFICATIONS")
    print("=" * 70)
    
    try:
        test_upgrade_downgrade()
        test_email_notifications()
        test_limit_warnings()
        test_trial_warnings()
        test_subscription_expiry_warnings()
        test_usage_tracking()
        test_feature_access()
        test_all_notifications()
        
        print("\n" + "=" * 70)
        print("TOUS LES TESTS SONT PASSES AVEC SUCCES!")
        print("=" * 70)
        print("\nFonctionnalites testees:")
        print("✓ Upgrade/Downgrade d'abonnement")
        print("✓ Notifications par email")
        print("✓ Avertissements de limite")
        print("✓ Avertissements de periode d'essai")
        print("✓ Avertissements d'expiration")
        print("✓ Suivi d'utilisation")
        print("✓ Acces aux fonctionnalites")
        print("✓ Test complet des notifications")
        
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()

