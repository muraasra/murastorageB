"""
Module de gestion de la réinitialisation de mot de passe
"""
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import hashlib
import hmac
import time

User = get_user_model()

class PasswordResetManager:
    """Gestionnaire de réinitialisation de mot de passe"""
    
    # Durée de validité du token (24 heures)
    TOKEN_VALIDITY_HOURS = 24
    
    @staticmethod
    def generate_reset_token(user):
        """
        Génère un token de réinitialisation de mot de passe
        """
        # Créer un token unique basé sur:
        # - User ID
        # - Email
        # - Timestamp
        # - Secret key de l'application
        
        timestamp = str(int(time.time()))
        data = f"{user.id}:{user.email}:{timestamp}"
        
        # Créer un hash HMAC
        token = hashlib.sha256(
            (data + settings.SECRET_KEY).encode()
        ).hexdigest()
        
        return f"{timestamp}:{token}"
    
    @staticmethod
    def verify_reset_token(token, email):
        """
        Vérifie si un token de réinitialisation est valide
        """
        try:
            # Séparer timestamp et hash
            parts = token.split(':')
            if len(parts) != 2:
                return None
            
            timestamp = parts[0]
            hash_part = parts[1]
            
            # Vérifier la date d'expiration
            token_time = int(timestamp)
            now_time = int(time.time())
            validity_seconds = PasswordResetManager.TOKEN_VALIDITY_HOURS * 3600
            
            if now_time - token_time > validity_seconds:
                return None  # Token expiré
            
            # Récupérer l'utilisateur
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None
            
            # Recréer le token attendu
            data = f"{user.id}:{user.email}:{timestamp}"
            expected_hash = hashlib.sha256(
                (data + settings.SECRET_KEY).encode()
            ).hexdigest()
            
            # Comparer les hashs
            if hash_part != expected_hash:
                return None  # Token invalide
            
            return user
            
        except Exception as e:
            print(f"Erreur lors de la vérification du token: {e}")
            return None
    
    @staticmethod
    def send_reset_email(user, token):
        """
        Envoie un email de réinitialisation de mot de passe
        """
        try:
            # Construire l'URL de réinitialisation
            # Utiliser l'URL de développement ou production selon l'environnement
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://murastorage.netlify.app')
            reset_url = f"{frontend_url}/reset-password?token={token}&email={user.email}"
            
            # Créer le contenu de l'email
            subject = 'Réinitialisation de votre mot de passe - MuraStock'
            message_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A6F 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0;">Réinitialisation de mot de passe</h1>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Bonjour {user.first_name or user.username},</p>
                        
                        <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte MuraStock.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A6F 100%); 
                                      color: white; 
                                      padding: 15px 40px; 
                                      text-decoration: none; 
                                      border-radius: 5px; 
                                      font-weight: bold;
                                      display: inline-block;">
                                Réinitialiser mon mot de passe
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #666;">ou copiez ce lien dans votre navigateur:</p>
                        <p style="word-break: break-all; font-size: 12px; color: #999; background: #fff; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                            {reset_url}
                        </p>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 30px;">
                            <strong>Important:</strong> Ce lien est valable pendant 24 heures. Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center;">
                            Cet email a été envoyé automatiquement par le système MuraStock.
                            Si vous rencontrez des problèmes, contactez le support.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Envoyer l'email
            send_mail(
                subject=subject,
                message='',  # Version texte vide (on utilise HTML)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=message_html,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de réinitialisation: {e}")
            return False

