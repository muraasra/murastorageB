"""
Management command Django pour envoyer les notifications automatiques
Usage: python manage.py send_notifications [--stock|--subscription|--summary|--all]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
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


class Command(BaseCommand):
    help = 'Envoyer les notifications automatiques (stocks, abonnements, résumés)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stock',
            action='store_true',
            help='Envoyer seulement les alertes de stock',
        )
        parser.add_argument(
            '--subscription',
            action='store_true',
            help='Envoyer seulement les alertes d\'abonnement',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Envoyer seulement les résumés quotidiens',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Envoyer toutes les notifications (par défaut)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            f"\n{'=' * 70}\n"
            f"NOTIFICATIONS AUTOMATIQUES - {timezone.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"{'=' * 70}\n"
        ))
        
        total_notifications = 0
        
        # Déterminer quelles notifications envoyer
        send_stock = options['stock'] or options['all'] or (not any([options['stock'], options['subscription'], options['summary']]))
        send_subscription = options['subscription'] or options['all'] or (not any([options['stock'], options['subscription'], options['summary']]))
        send_summary = options['summary'] or options['all'] or (not any([options['stock'], options['subscription'], options['summary']]))
        
        # 1. Alertes de stock
        if send_stock:
            self.stdout.write("\n=== 1. Vérification des alertes de stock ===")
            
            # Alertes de stock faible
            low_stock_count = 0
            try:
                if check_low_stock_alerts():
                    low_stock_count = 1
                    total_notifications += 1
                    self.stdout.write(self.style.SUCCESS("✓ Alertes de stock faible envoyées"))
                else:
                    self.stdout.write("  Aucun stock faible détecté")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la vérification des stocks faibles: {e}"))
            
            # Alertes de rupture de stock
            stock_out_count = 0
            try:
                if check_stock_out_alerts():
                    stock_out_count = 1
                    total_notifications += 1
                    self.stdout.write(self.style.SUCCESS("✓ Alertes de rupture de stock envoyées"))
                else:
                    self.stdout.write("  Aucune rupture de stock détectée")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la vérification des ruptures: {e}"))
            
            self.stdout.write(f"  Total alertes de stock: {low_stock_count + stock_out_count}")
        
        # 2. Alertes d'abonnement
        if send_subscription:
            self.stdout.write("\n=== 2. Vérification des alertes d'abonnement ===")
            
            subscription_alerts = 0
            try:
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
                
                total_notifications += subscription_alerts
                if subscription_alerts > 0:
                    self.stdout.write(self.style.SUCCESS(f"✓ {subscription_alerts} alerte(s) d'abonnement envoyée(s)"))
                else:
                    self.stdout.write("  Aucune alerte d'abonnement nécessaire")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de la vérification des abonnements: {e}"))
        
        # 3. Résumés quotidiens
        if send_summary:
            self.stdout.write("\n=== 3. Résumés quotidiens des stocks ===")
            
            daily_summaries = 0
            try:
                for entreprise in Entreprise.objects.all():
                    if send_daily_stock_summary(entreprise):
                        daily_summaries += 1
                
                if daily_summaries > 0:
                    self.stdout.write(self.style.SUCCESS(f"✓ {daily_summaries} résumé(s) quotidien(s) envoyé(s)"))
                else:
                    self.stdout.write("  Aucun résumé quotidien envoyé")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur lors de l'envoi des résumés: {e}"))
        
        # Résumé final
        self.stdout.write(self.style.SUCCESS(
            f"\n{'=' * 70}\n"
            f"RÉSUMÉ DES NOTIFICATIONS\n"
            f"{'=' * 70}\n"
            f"📧 Total d'alertes envoyées: {total_notifications}\n"
            f"📊 Résumés quotidiens: {daily_summaries if send_summary else 0}\n"
            f"⏰ Heure d'exécution: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"{'=' * 70}\n"
        ))

