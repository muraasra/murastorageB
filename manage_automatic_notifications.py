"""
Configuration des notifications automatiques
Script à exécuter tous les 2 jours via cron ou scheduler
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import Entreprise
from core.stock_notifications import (
    check_low_stock_alerts,
    check_stock_out_alerts,
    send_daily_stock_summary
)
from core.subscription_notifications import (
    check_and_send_limit_warnings,
    check_and_send_trial_warnings,
    check_and_send_subscription_expiry_warnings
)

def run_automatic_notifications():
    """
    Exécuter toutes les notifications automatiques
    À programmer tous les 2 jours
    """
    print("=" * 70)
    print("NOTIFICATIONS AUTOMATIQUES - " + timezone.now().strftime('%d/%m/%Y %H:%M'))
    print("=" * 70)
    
    total_notifications = 0
    
    # 1. Vérifier les alertes de stock
    print("\n=== 1. Vérification des alertes de stock ===")
    
    # Alertes de stock faible
    low_stock_count = 0
    if check_low_stock_alerts():
        low_stock_count = 1
        total_notifications += 1
    
    # Alertes de rupture de stock
    stock_out_count = 0
    if check_stock_out_alerts():
        stock_out_count = 1
        total_notifications += 1
    
    print(f"Alertes de stock: {low_stock_count + stock_out_count}")
    
    # 2. Vérifier les alertes d'abonnement
    print("\n=== 2. Vérification des alertes d'abonnement ===")
    
    subscription_alerts = 0
    for entreprise in Entreprise.objects.all():
        # Vérifier les limites
        if check_and_send_limit_warnings(entreprise):
            subscription_alerts += 1
        
        # Vérifier la période d'essai
        if check_and_send_trial_warnings(entreprise):
            subscription_alerts += 1
        
        # Vérifier l'expiration
        if check_and_send_subscription_expiry_warnings(entreprise):
            subscription_alerts += 1
    
    print(f"Alertes d'abonnement: {subscription_alerts}")
    total_notifications += subscription_alerts
    
    # 3. Envoyer les résumés quotidiens des stocks
    print("\n=== 3. Résumés quotidiens des stocks ===")
    
    daily_summaries = 0
    for entreprise in Entreprise.objects.all():
        if send_daily_stock_summary(entreprise):
            daily_summaries += 1
    
    print(f"Résumés quotidiens envoyés: {daily_summaries}")
    
    # Résumé final
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES NOTIFICATIONS")
    print("=" * 70)
    print(f"Total d'alertes envoyees: {total_notifications}")
    print(f"Resumes quotidiens: {daily_summaries}")
    print(f"Heure d'execution: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    return total_notifications

def run_stock_alerts_only():
    """
    Exécuter seulement les alertes de stock (pour tests)
    """
    print("=== ALERTES DE STOCK SEULEMENT ===")
    
    # Vérifier les stocks faibles
    low_stock_alerts = check_low_stock_alerts()
    
    # Vérifier les ruptures de stock
    stock_out_alerts = check_stock_out_alerts()
    
    total_alerts = (1 if low_stock_alerts else 0) + (1 if stock_out_alerts else 0)
    
    print(f"Alertes de stock envoyées: {total_alerts}")
    return total_alerts

def run_subscription_alerts_only():
    """
    Exécuter seulement les alertes d'abonnement (pour tests)
    """
    print("=== ALERTES D'ABONNEMENT SEULEMENT ===")
    
    subscription_alerts = 0
    for entreprise in Entreprise.objects.all():
        if check_and_send_limit_warnings(entreprise):
            subscription_alerts += 1
        if check_and_send_trial_warnings(entreprise):
            subscription_alerts += 1
        if check_and_send_subscription_expiry_warnings(entreprise):
            subscription_alerts += 1
    
    print(f"Alertes d'abonnement envoyées: {subscription_alerts}")
    return subscription_alerts

def run_daily_summaries_only():
    """
    Exécuter seulement les résumés quotidiens (pour tests)
    """
    print("=== RÉSUMÉS QUOTIDIENS SEULEMENT ===")
    
    daily_summaries = 0
    for entreprise in Entreprise.objects.all():
        if send_daily_stock_summary(entreprise):
            daily_summaries += 1
    
    print(f"Résumés quotidiens envoyés: {daily_summaries}")
    return daily_summaries

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'stock':
            run_stock_alerts_only()
        elif mode == 'subscription':
            run_subscription_alerts_only()
        elif mode == 'summary':
            run_daily_summaries_only()
        elif mode == 'all':
            run_automatic_notifications()
        else:
            print("Usage: python manage_notifications.py [stock|subscription|summary|all]")
            print("  stock: Alertes de stock seulement")
            print("  subscription: Alertes d'abonnement seulement")
            print("  summary: Résumés quotidiens seulement")
            print("  all: Toutes les notifications (par défaut)")
    else:
        # Mode par défaut: toutes les notifications
        run_automatic_notifications()

