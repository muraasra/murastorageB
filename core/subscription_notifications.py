"""
Système de notifications par email pour les abonnements
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EntrepriseSubscription, SubscriptionPlan, Entreprise, User

def send_subscription_notification_email(entreprise, notification_type, data=None):
    """
    Envoyer une notification par email au SuperAdmin de l'entreprise
    
    Args:
        entreprise: Instance de l'entreprise
        notification_type: Type de notification ('upgrade', 'downgrade', 'limit_warning', 'trial_ending', 'subscription_expiring')
        data: Données supplémentaires pour le template
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
        
        # Récupérer l'abonnement actuel
        subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
        if not subscription:
            print(f"Aucun abonnement trouvé pour l'entreprise {entreprise.nom}")
            return False
        
        # Préparer les données pour le template
        context = {
            'entreprise': entreprise,
            'superadmin': superadmin,
            'subscription': subscription,
            'plan': subscription.plan,
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
            'data': data or {}
        }
        
        # Déterminer le template et le sujet selon le type de notification
        templates = {
            'upgrade': {
                'template': 'emails/subscription_upgrade.html',
                'subject': f'[StoRage] Mise à niveau vers {subscription.plan.display_name}',
                'text_template': 'emails/subscription_upgrade.txt'
            },
            'downgrade': {
                'template': 'emails/subscription_downgrade.html',
                'subject': f'[StoRage] Rétrogradation vers {subscription.plan.display_name}',
                'text_template': 'emails/subscription_downgrade.txt'
            },
            'limit_warning': {
                'template': 'emails/limit_warning.html',
                'subject': f'[StoRage] Alerte: Limite atteinte - {data.get("resource_type", "")}',
                'text_template': 'emails/limit_warning.txt'
            },
            'trial_ending': {
                'template': 'emails/trial_ending.html',
                'subject': f'[StoRage] Période d\'essai se termine bientôt',
                'text_template': 'emails/trial_ending.txt'
            },
            'subscription_expiring': {
                'template': 'emails/subscription_expiring.html',
                'subject': f'[StoRage] Abonnement expire bientôt',
                'text_template': 'emails/subscription_expiring.txt'
            }
        }
        
        template_info = templates.get(notification_type)
        if not template_info:
            print(f"Type de notification inconnu: {notification_type}")
            return False
        
        # Rendre le template HTML
        html_message = render_to_string(template_info['template'], context)
        
        # Rendre le template texte (fallback)
        try:
            text_message = render_to_string(template_info['text_template'], context)
        except:
            text_message = f"Notification {notification_type} pour {entreprise.nom}"
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=template_info['subject'],
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[superadmin.email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        print(f"Email de notification '{notification_type}' envoyé à {superadmin.email}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        return False

def check_and_send_limit_warnings(entreprise):
    """
    Vérifier les limites et envoyer des avertissements si nécessaire
    """
    from .subscription_utils import get_current_usage, get_subscription_limits
    
    try:
        usage = get_current_usage(entreprise)
        limits = get_subscription_limits(entreprise)
        
        warnings_sent = []
        
        # Vérifier chaque type de limite
        limits_to_check = [
            ('users', usage['users_count'], limits['max_users']),
            ('boutiques', usage['boutiques_count'], limits['max_boutiques']),
            ('produits', usage['produits_count'], limits['max_produits']),
            ('factures', usage['factures_count'], limits['max_factures_per_month'])
        ]
        
        for resource_type, current, limit in limits_to_check:
            if limit and limit < 999999:  # Pas illimité
                percentage = (current / limit) * 100
                
                # Envoyer un avertissement à 80% et 95%
                if percentage >= 95 and f"{resource_type}_95" not in warnings_sent:
                    send_subscription_notification_email(
                        entreprise, 
                        'limit_warning',
                        {
                            'resource_type': resource_type,
                            'current': current,
                            'limit': limit,
                            'percentage': percentage,
                            'warning_level': 'critical'
                        }
                    )
                    warnings_sent.append(f"{resource_type}_95")
                    
                elif percentage >= 80 and f"{resource_type}_80" not in warnings_sent:
                    send_subscription_notification_email(
                        entreprise, 
                        'limit_warning',
                        {
                            'resource_type': resource_type,
                            'current': current,
                            'limit': limit,
                            'percentage': percentage,
                            'warning_level': 'warning'
                        }
                    )
                    warnings_sent.append(f"{resource_type}_80")
        
        return len(warnings_sent) > 0
        
    except Exception as e:
        print(f"Erreur lors de la vérification des limites: {str(e)}")
        return False

def check_and_send_trial_warnings(entreprise):
    """
    Vérifier la période d'essai et envoyer des avertissements
    """
    try:
        subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
        if not subscription or not subscription.trial_end_date:
            return False
        
        now = timezone.now()
        trial_end = subscription.trial_end_date
        
        # Calculer les jours restants
        days_remaining = (trial_end - now).days
        
        # Envoyer des avertissements à 7 jours, 3 jours et 1 jour
        if days_remaining == 7:
            send_subscription_notification_email(
                entreprise, 
                'trial_ending',
                {'days_remaining': 7}
            )
            return True
        elif days_remaining == 3:
            send_subscription_notification_email(
                entreprise, 
                'trial_ending',
                {'days_remaining': 3}
            )
            return True
        elif days_remaining == 1:
            send_subscription_notification_email(
                entreprise, 
                'trial_ending',
                {'days_remaining': 1}
            )
            return True
        
        return False
        
    except Exception as e:
        print(f"Erreur lors de la vérification de la période d'essai: {str(e)}")
        return False

def check_and_send_subscription_expiry_warnings(entreprise):
    """
    Vérifier l'expiration de l'abonnement et envoyer des avertissements
    """
    try:
        subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
        if not subscription or not subscription.end_date:
            return False
        
        now = timezone.now()
        end_date = subscription.end_date
        
        # Calculer les jours restants
        days_remaining = (end_date - now).days
        
        # Envoyer des avertissements à 30 jours, 7 jours et 1 jour
        if days_remaining == 30:
            send_subscription_notification_email(
                entreprise, 
                'subscription_expiring',
                {'days_remaining': 30}
            )
            return True
        elif days_remaining == 7:
            send_subscription_notification_email(
                entreprise, 
                'subscription_expiring',
                {'days_remaining': 7}
            )
            return True
        elif days_remaining == 1:
            send_subscription_notification_email(
                entreprise, 
                'subscription_expiring',
                {'days_remaining': 1}
            )
            return True
        
        return False
        
    except Exception as e:
        print(f"Erreur lors de la vérification de l'expiration: {str(e)}")
        return False

def process_subscription_change(entreprise, new_plan_id, change_type='upgrade'):
    """
    Traiter un changement d'abonnement (upgrade ou downgrade)
    
    Args:
        entreprise: Instance de l'entreprise
        new_plan_id: ID du nouveau plan
        change_type: 'upgrade' ou 'downgrade'
    """
    try:
        # Récupérer l'ancien abonnement
        subscription = EntrepriseSubscription.objects.filter(entreprise=entreprise).first()
        if not subscription:
            return False, "Aucun abonnement trouvé"
        
        old_plan = subscription.plan
        
        # Récupérer le nouveau plan
        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return False, "Plan invalide"
        
        # Vérifier si c'est vraiment un upgrade ou downgrade
        if change_type == 'upgrade' and new_plan.price_monthly <= old_plan.price_monthly:
            return False, "Ce n'est pas un upgrade"
        elif change_type == 'downgrade' and new_plan.price_monthly >= old_plan.price_monthly:
            return False, "Ce n'est pas un downgrade"
        
        # Effectuer le changement
        subscription.plan = new_plan
        subscription.updated_at = timezone.now()
        
        # Si c'est un upgrade, prolonger l'abonnement
        if change_type == 'upgrade':
            if subscription.end_date:
                subscription.end_date = subscription.end_date + timedelta(days=30)
            else:
                subscription.end_date = timezone.now() + timedelta(days=30)
        
        subscription.save()
        
        # Envoyer l'email de notification
        send_subscription_notification_email(
            entreprise, 
            change_type,
            {
                'old_plan': old_plan,
                'new_plan': new_plan,
                'change_type': change_type
            }
        )
        
        return True, f"Changement vers {new_plan.display_name} effectué avec succès"
        
    except Exception as e:
        return False, f"Erreur lors du changement: {str(e)}"











