import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerification, User, Entreprise, Boutique

def generate_verification_code():
    """Génère un code de vérification à 6 chiffres"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(user, entreprise):
    """Envoie l'email de vérification avec le code à 6 chiffres"""
    try:
        # Générer un nouveau code de vérification
        verification_code = generate_verification_code()
        
        # Créer ou mettre à jour l'enregistrement de vérification
        verification, created = EmailVerification.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={
                'verification_code': verification_code,
                'expires_at': timezone.now() + timedelta(minutes=15)
            }
        )
        
        if not created:
            # Mettre à jour le code existant
            verification.verification_code = verification_code
            verification.expires_at = timezone.now() + timedelta(minutes=15)
            verification.status = 'pending'
            verification.verified_at = None
            verification.save()
        
        # Préparer le contexte pour le template
        context = {
            'user': user,
            'entreprise': entreprise,
            'verification_code': verification_code
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/verification_email.html', context)
        
        # Envoyer l'email
        send_mail(
            subject='Vérification de votre email - StoRage',
            message=f'Votre code de vérification est : {verification_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True, verification_code
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de vérification: {e}")
        return False, str(e)

def send_confirmation_email(user, entreprise, boutique):
    """Envoie l'email de confirmation après vérification réussie"""
    try:
        # Préparer le contexte pour le template
        context = {
            'user': user,
            'entreprise': entreprise,
            'boutique': boutique
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/confirmation_email.html', context)
        
        # Envoyer l'email
        send_mail(
            subject='🎉 Félicitations ! Votre entreprise est créée - StoRage',
            message=f'Félicitations {user.first_name} ! Votre entreprise {entreprise.nom} est maintenant active.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de confirmation: {e}")
        return False

def send_transfer_notification_emails(transfer_data):
    """Envoie 3 emails lors d'un transfert de stock :
    1. Confirmation à l'utilisateur qui initie le transfert
    2. Notification au superadmin de l'entreprise
    3. Notification à l'utilisateur qui gère l'entrepôt de destination
    """
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings
        from .models import User, Boutique
        
        # Récupérer les données du transfert
        user_initiateur = transfer_data['user_initiateur']
        entreprise = transfer_data['entreprise']
        boutique_source = transfer_data['boutique_source']
        boutique_destination = transfer_data['boutique_destination']
        produit = transfer_data['produit']
        quantite = transfer_data['quantite']
        motif = transfer_data['motif']
        reference_transfert = transfer_data['reference_transfert']
        
        # 1. Récupérer le superadmin de l'entreprise
        superadmin = User.objects.filter(
            entreprise=entreprise, 
            role='superadmin'
        ).first()
        
        # 2. Récupérer l'utilisateur qui gère l'entrepôt de destination
        gestionnaire_destination = User.objects.filter(
            boutique=boutique_destination,
            entreprise=entreprise
        ).first()
        
        # Contexte commun pour tous les emails
        base_context = {
            'entreprise': entreprise,
            'boutique_source': boutique_source,
            'boutique_destination': boutique_destination,
            'produit': produit,
            'quantite': quantite,
            'motif': motif,
            'reference_transfert': reference_transfert,
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
        }
        
        # 1. EMAIL DE CONFIRMATION À L'INITIATEUR
        if user_initiateur and user_initiateur.email:
            context_initiateur = {
                **base_context,
                'user': user_initiateur,
                'email_type': 'confirmation'
            }
            
            html_message_initiateur = render_to_string('emails/transfer_confirmation.html', context_initiateur)
            
            email_initiateur = EmailMultiAlternatives(
                subject=f'✅ Confirmation de Transfert - {reference_transfert}',
                body=f'Bonjour {user_initiateur.first_name},\n\nVotre transfert de {quantite} unité(s) de {produit} vers {boutique_destination.nom} a été effectué avec succès.\n\nRéférence: {reference_transfert}\n\nCordialement,\nL\'équipe StoRage',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_initiateur.email]
            )
            email_initiateur.attach_alternative(html_message_initiateur, "text/html")
            email_initiateur.send(fail_silently=False)
            print(f"✅ Email de confirmation envoyé à {user_initiateur.email}")
        
        # 2. EMAIL AU SUPERADMIN
        if superadmin and superadmin.email and superadmin.email != user_initiateur.email:
            context_superadmin = {
                **base_context,
                'user': superadmin,
                'email_type': 'superadmin_notification'
            }
            
            html_message_superadmin = render_to_string('emails/transfer_superadmin.html', context_superadmin)
            
            email_superadmin = EmailMultiAlternatives(
                subject=f'📦 Transfert de Stock - {reference_transfert}',
                body=f'Bonjour {superadmin.first_name},\n\nUn transfert de stock a été effectué dans votre entreprise:\n\n- Produit: {produit}\n- Quantité: {quantite}\n- De: {boutique_source.nom}\n- Vers: {boutique_destination.nom}\n- Par: {user_initiateur.first_name} {user_initiateur.last_name}\n- Référence: {reference_transfert}\n\nCordialement,\nL\'équipe StoRage',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[superadmin.email]
            )
            email_superadmin.attach_alternative(html_message_superadmin, "text/html")
            email_superadmin.send(fail_silently=False)
            print(f"✅ Email de notification envoyé au superadmin {superadmin.email}")
        
        # 3. EMAIL AU GESTIONNAIRE DE L'ENTREPÔT DE DESTINATION
        if gestionnaire_destination and gestionnaire_destination.email and gestionnaire_destination.email != user_initiateur.email:
            context_gestionnaire = {
                **base_context,
                'user': gestionnaire_destination,
                'email_type': 'destination_notification'
            }
            
            html_message_gestionnaire = render_to_string('emails/transfer_destination.html', context_gestionnaire)
            
            email_gestionnaire = EmailMultiAlternatives(
                subject=f'📥 Réception de Stock - {reference_transfert}',
                body=f'Bonjour {gestionnaire_destination.first_name},\n\nUn transfert de stock arrive dans votre entrepôt:\n\n- Produit: {produit}\n- Quantité: {quantite}\n- Depuis: {boutique_source.nom}\n- Référence: {reference_transfert}\n\nCordialement,\nL\'équipe StoRage',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[gestionnaire_destination.email]
            )
            email_gestionnaire.attach_alternative(html_message_gestionnaire, "text/html")
            email_gestionnaire.send(fail_silently=False)
            print(f"✅ Email de réception envoyé au gestionnaire {gestionnaire_destination.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi des emails de transfert: {e}")
        return False

def verify_email_code(user, code):
    """Vérifie le code de vérification email"""
    try:
        verification = EmailVerification.objects.filter(
            user=user,
            verification_code=code,
            status='pending'
        ).first()
        
        if not verification:
            return False, "Code de vérification invalide"
        
        if verification.is_expired():
            verification.mark_as_expired()
            return False, "Code de vérification expiré"
        
        # Marquer comme vérifié
        verification.mark_as_verified()
        
        return True, "Email vérifié avec succès"
        
    except Exception as e:
        return False, f"Erreur lors de la vérification: {str(e)}"














