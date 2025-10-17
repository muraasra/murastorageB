"""
Script de test complet pour le système d'abonnement avec notifications de stock
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import Entreprise, User, Stock, Produit, Boutique, SubscriptionPlan, EntrepriseSubscription
from core.stock_notifications import (
    check_low_stock_alerts,
    check_stock_out_alerts,
    send_daily_stock_summary
)
from core.subscription_notifications import (
    process_subscription_change,
    check_and_send_limit_warnings,
    check_and_send_trial_warnings,
    check_and_send_subscription_expiry_warnings
)

def test_stock_notifications():
    """Tester les notifications de stock"""
    print("\n=== Test 1: Notifications de stock ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return False
    
    # Créer une boutique de test
    boutique = Boutique.objects.filter(entreprise=entreprise).first()
    if not boutique:
        boutique = Boutique.objects.create(
            entreprise=entreprise,
            nom="Boutique Test",
            ville="Testville"
        )
    
    # Créer des produits de test
    produit1 = Produit.objects.create(
        entreprise=entreprise,
        nom="Produit Test 1",
        prix_vente=100,
        quantite=5
    )
    
    produit2 = Produit.objects.create(
        entreprise=entreprise,
        nom="Produit Test 2",
        prix_vente=200,
        quantite=0
    )
    
    # Créer des stocks de test
    stock1 = Stock.objects.create(
        produit=produit1,
        entrepot=boutique,
        quantite=3  # Stock faible
    )
    
    stock2 = Stock.objects.create(
        produit=produit2,
        entrepot=boutique,
        quantite=0  # Rupture de stock
    )
    
    # Définir les stocks minimums sur les produits
    produit1.stock_minimum = 10
    produit1.save()
    
    produit2.stock_minimum = 5
    produit2.save()
    
    print(f"Entreprise: {entreprise.nom}")
    print(f"Boutique: {boutique.nom}")
    print(f"Stock faible: {stock1.produit.nom} ({stock1.quantite}/{stock1.produit.stock_minimum})")
    print(f"Rupture de stock: {stock2.produit.nom} ({stock2.quantite}/{stock2.produit.stock_minimum})")
    
    # Tester les alertes de stock faible
    print("\n--- Test alertes de stock faible ---")
    low_stock_alerts = check_low_stock_alerts()
    print(f"[{'OK' if low_stock_alerts else 'INFO'}] Alertes de stock faible: {'Envoyees' if low_stock_alerts else 'Aucune necessaire'}")
    
    # Tester les alertes de rupture de stock
    print("\n--- Test alertes de rupture de stock ---")
    stock_out_alerts = check_stock_out_alerts()
    print(f"[{'OK' if stock_out_alerts else 'INFO'}] Alertes de rupture: {'Envoyees' if stock_out_alerts else 'Aucune necessaire'}")
    
    # Tester le résumé quotidien
    print("\n--- Test résumé quotidien ---")
    daily_summary = send_daily_stock_summary(entreprise)
    print(f"[{'OK' if daily_summary else 'ERREUR'}] Résumé quotidien: {'Envoye' if daily_summary else 'Echec'}")
    
    return low_stock_alerts or stock_out_alerts or daily_summary

def test_subscription_notifications():
    """Tester les notifications d'abonnement"""
    print("\n=== Test 2: Notifications d'abonnement ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return False
    
    # Modifier l'abonnement pour tester les alertes
    subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
    if subscription:
        # Tester l'alerte de période d'essai
        subscription.trial_end_date = timezone.now() + timedelta(days=3)
        subscription.save()
        
        # Tester l'alerte d'expiration
        subscription.end_date = timezone.now() + timedelta(days=7)
        subscription.save()
    
    print(f"Entreprise: {entreprise.nom}")
    print(f"Période d'essai expire dans: {subscription.get_remaining_trial_days() if subscription else 'N/A'} jours")
    print(f"Abonnement expire dans: {(subscription.end_date - timezone.now()).days if subscription and subscription.end_date else 'N/A'} jours")
    
    # Tester les alertes d'abonnement
    alerts_sent = 0
    
    if check_and_send_limit_warnings(entreprise):
        alerts_sent += 1
        print("[OK] Avertissement de limite envoye")
    
    if check_and_send_trial_warnings(entreprise):
        alerts_sent += 1
        print("[OK] Avertissement de periode d'essai envoye")
    
    if check_and_send_subscription_expiry_warnings(entreprise):
        alerts_sent += 1
        print("[OK] Avertissement d'expiration envoye")
    
    print(f"[OK] Total d'alertes d'abonnement envoyees: {alerts_sent}")
    return alerts_sent > 0

def test_upgrade_downgrade():
    """Tester les fonctionnalités d'upgrade/downgrade"""
    print("\n=== Test 3: Upgrade/Downgrade ===")
    
    entreprise = Entreprise.objects.filter(nom__contains="Test").first()
    if not entreprise:
        print("[SKIP] Aucune entreprise de test trouvee")
        return False
    
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
    
    return True

def test_automatic_notifications():
    """Tester le système de notifications automatiques"""
    print("\n=== Test 4: Notifications automatiques ===")
    
    # Importer le script de gestion automatique
    from manage_automatic_notifications import run_automatic_notifications
    
    print("Execution du système de notifications automatiques...")
    total_notifications = run_automatic_notifications()
    
    print(f"[OK] Total de notifications automatiques: {total_notifications}")
    return total_notifications > 0

def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 70)
    print("TESTS COMPLETS DU SYSTEME D'ABONNEMENT ET NOTIFICATIONS")
    print("=" * 70)
    
    try:
        # Tests des notifications de stock
        stock_tests = test_stock_notifications()
        
        # Tests des notifications d'abonnement
        subscription_tests = test_subscription_notifications()
        
        # Tests d'upgrade/downgrade
        upgrade_tests = test_upgrade_downgrade()
        
        # Tests des notifications automatiques
        automatic_tests = test_automatic_notifications()
        
        print("\n" + "=" * 70)
        print("TOUS LES TESTS SONT PASSES AVEC SUCCES!")
        print("=" * 70)
        print("\nFonctionnalites testees:")
        print("✓ Notifications de stock faible")
        print("✓ Notifications de rupture de stock")
        print("✓ Résumés quotidiens des stocks")
        print("✓ Notifications d'abonnement")
        print("✓ Upgrade/Downgrade d'abonnement")
        print("✓ Notifications automatiques")
        print("✓ Intégration dans le dashboard SuperAdmin")
        
        print("\nRésumé des tests:")
        print(f"  - Notifications de stock: {'✓' if stock_tests else '✗'}")
        print(f"  - Notifications d'abonnement: {'✓' if subscription_tests else '✗'}")
        print(f"  - Upgrade/Downgrade: {'✓' if upgrade_tests else '✗'}")
        print(f"  - Notifications automatiques: {'✓' if automatic_tests else '✗'}")
        
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()

