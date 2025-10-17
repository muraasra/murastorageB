"""
Système de notifications pour les alertes de stock
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import Stock, Entreprise, User
from .subscription_notifications import send_subscription_notification_email

def check_low_stock_alerts():
    """
    Vérifier tous les stocks inférieurs au minimum et envoyer des alertes
    """
    try:
        # Récupérer tous les stocks avec quantité inférieure au minimum
        low_stocks = Stock.objects.filter(
            quantite__lt=models.F('produit__stock_minimum'),
            quantite__gt=0  # Exclure les stocks à zéro (rupture totale)
        ).select_related('produit', 'entrepot', 'entrepot__entreprise')
        
        if not low_stocks.exists():
            print("Aucun stock faible détecté")
            return False
        
        # Grouper par entreprise
        entreprises_with_low_stocks = {}
        for stock in low_stocks:
            entreprise = stock.entrepot.entreprise
            if entreprise not in entreprises_with_low_stocks:
                entreprises_with_low_stocks[entreprise] = []
            entreprises_with_low_stocks[entreprise].append(stock)
        
        # Envoyer des notifications pour chaque entreprise
        notifications_sent = 0
        for entreprise, stocks in entreprises_with_low_stocks.items():
            if send_low_stock_notification(entreprise, stocks):
                notifications_sent += 1
        
        print(f"Notifications de stock faible envoyées à {notifications_sent} entreprise(s)")
        return notifications_sent > 0
        
    except Exception as e:
        print(f"Erreur lors de la vérification des stocks faibles: {str(e)}")
        return False

def send_low_stock_notification(entreprise, low_stocks):
    """
    Envoyer une notification de stock faible à l'entreprise
    """
    try:
        # Récupérer le SuperAdmin de l'entreprise
        superadmin = User.objects.filter(
            entreprise=entreprise, 
            role='superadmin'
        ).first()
        
        if not superadmin:
            print(f"Aucun SuperAdmin trouvé pour l'entreprise {entreprise.nom}")
            return False
        
        # Préparer les données pour le template
        context = {
            'entreprise': entreprise,
            'superadmin': superadmin,
            'low_stocks': low_stocks,
            'total_low_stocks': len(low_stocks),
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
            'alert_date': timezone.now().strftime('%d/%m/%Y à %H:%M')
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/low_stock_alert.html', context)
        
        # Rendre le template texte (fallback)
        try:
            text_message = render_to_string('emails/low_stock_alert.txt', context)
        except:
            text_message = f"Alerte de stock faible pour {entreprise.nom}"
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=f'[StoRage] Alerte: Stock faible détecté ({len(low_stocks)} produit(s))',
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[superadmin.email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        print(f"Email d'alerte de stock faible envoyé à {superadmin.email}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email d'alerte de stock: {str(e)}")
        return False

def check_stock_out_alerts():
    """
    Vérifier les ruptures de stock (quantité = 0) et envoyer des alertes
    """
    try:
        # Récupérer tous les stocks en rupture
        out_of_stocks = Stock.objects.filter(
            quantite=0,
            produit__stock_minimum__gt=0  # Seulement ceux qui ont un minimum défini
        ).select_related('produit', 'entrepot', 'entrepot__entreprise')
        
        if not out_of_stocks.exists():
            print("Aucune rupture de stock détectée")
            return False
        
        # Grouper par entreprise
        entreprises_with_out_stocks = {}
        for stock in out_of_stocks:
            entreprise = stock.entrepot.entreprise
            if entreprise not in entreprises_with_out_stocks:
                entreprises_with_out_stocks[entreprise] = []
            entreprises_with_out_stocks[entreprise].append(stock)
        
        # Envoyer des notifications pour chaque entreprise
        notifications_sent = 0
        for entreprise, stocks in entreprises_with_out_stocks.items():
            if send_stock_out_notification(entreprise, stocks):
                notifications_sent += 1
        
        print(f"Notifications de rupture de stock envoyées à {notifications_sent} entreprise(s)")
        return notifications_sent > 0
        
    except Exception as e:
        print(f"Erreur lors de la vérification des ruptures de stock: {str(e)}")
        return False

def send_stock_out_notification(entreprise, out_of_stocks):
    """
    Envoyer une notification de rupture de stock à l'entreprise
    """
    try:
        # Récupérer le SuperAdmin de l'entreprise
        superadmin = User.objects.filter(
            entreprise=entreprise, 
            role='superadmin'
        ).first()
        
        if not superadmin:
            print(f"Aucun SuperAdmin trouvé pour l'entreprise {entreprise.nom}")
            return False
        
        # Préparer les données pour le template
        context = {
            'entreprise': entreprise,
            'superadmin': superadmin,
            'out_of_stocks': out_of_stocks,
            'total_out_stocks': len(out_of_stocks),
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
            'alert_date': timezone.now().strftime('%d/%m/%Y à %H:%M')
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/stock_out_alert.html', context)
        
        # Rendre le template texte (fallback)
        try:
            text_message = render_to_string('emails/stock_out_alert.txt', context)
        except:
            text_message = f"Alerte de rupture de stock pour {entreprise.nom}"
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=f'[StoRage] URGENT: Rupture de stock ({len(out_of_stocks)} produit(s))',
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[superadmin.email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        print(f"Email d'alerte de rupture de stock envoyé à {superadmin.email}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email d'alerte de rupture: {str(e)}")
        return False

def send_daily_stock_summary(entreprise):
    """
    Envoyer un résumé quotidien des stocks à l'entreprise
    """
    try:
        # Récupérer le SuperAdmin de l'entreprise
        superadmin = User.objects.filter(
            entreprise=entreprise, 
            role='superadmin'
        ).first()
        
        if not superadmin:
            return False
        
        # Récupérer tous les stocks de l'entreprise
        all_stocks = Stock.objects.filter(
            entrepot__entreprise=entreprise
        ).select_related('produit', 'entrepot')
        
        # Calculer les statistiques
        total_products = all_stocks.count()
        low_stocks = all_stocks.filter(quantite__lt=models.F('produit__stock_minimum'), quantite__gt=0).count()
        out_of_stocks = all_stocks.filter(quantite=0).count()
        normal_stocks = total_products - low_stocks - out_of_stocks
        
        # Préparer les données pour le template
        context = {
            'entreprise': entreprise,
            'superadmin': superadmin,
            'total_products': total_products,
            'low_stocks': low_stocks,
            'out_of_stocks': out_of_stocks,
            'normal_stocks': normal_stocks,
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
            'summary_date': timezone.now().strftime('%d/%m/%Y')
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/daily_stock_summary.html', context)
        
        # Rendre le template texte (fallback)
        try:
            text_message = render_to_string('emails/daily_stock_summary.txt', context)
        except:
            text_message = f"Résumé quotidien des stocks pour {entreprise.nom}"
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=f'[StoRage] Résumé quotidien des stocks - {entreprise.nom}',
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[superadmin.email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        print(f"Résumé quotidien des stocks envoyé à {superadmin.email}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi du résumé quotidien: {str(e)}")
        return False

def run_all_stock_checks():
    """
    Exécuter toutes les vérifications de stock
    """
    print("=== Vérification des alertes de stock ===")
    
    # Vérifier les stocks faibles
    low_stock_alerts = check_low_stock_alerts()
    
    # Vérifier les ruptures de stock
    stock_out_alerts = check_stock_out_alerts()
    
    # Résumé
    total_alerts = (1 if low_stock_alerts else 0) + (1 if stock_out_alerts else 0)
    print(f"Total d'alertes envoyées: {total_alerts}")
    
    return total_alerts > 0

