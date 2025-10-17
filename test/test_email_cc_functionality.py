#!/usr/bin/env python3
"""
Test spécifique de la fonctionnalité CC email
- Vérifier que l'email est envoyé avec CC au SuperAdmin
- Tester avec différents scénarios
"""

import os
import sys
import django

# Configuration Django
sys.path.append('/path/to/your/django/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()

def test_email_cc_functionality():
    """Test de la fonctionnalité CC email."""
    print("📧 TEST FONCTIONNALITÉ CC EMAIL")
    print("=" * 40)
    
    try:
        # Récupérer l'utilisateur créé
        user = User.objects.get(email='wilfriedtayouf7@gmail.com')
        entreprise = user.entreprise
        boutique = user.boutique
        
        # Récupérer le SuperAdmin
        superadmin = User.objects.filter(entreprise=entreprise, role='superadmin').first()
        
        print(f"👤 Utilisateur: {user.first_name} {user.last_name}")
        print(f"📧 Email utilisateur: {user.email}")
        print(f"🏢 Entreprise: {entreprise.nom}")
        print(f"🏪 Boutique: {boutique.nom}")
        print(f"👑 SuperAdmin: {superadmin.first_name if superadmin else 'Non trouvé'}")
        print(f"📧 Email SuperAdmin: {superadmin.email if superadmin else 'Non trouvé'}")
        
        # Simuler l'envoi d'email avec CC
        print(f"\n📤 SIMULATION ENVOI EMAIL AVEC CC")
        print("=" * 40)
        
        # Contexte pour le template
        context = {
            'user': user,
            'entreprise': entreprise,
            'boutique': boutique,
            'temp_password': 'TempPassword123!',
            'login_url': f"{settings.FRONTEND_URL}/connexion?entreprise_id={entreprise.id_entreprise}",
            'site_name': 'StoRage',
            'site_url': settings.FRONTEND_URL,
            'superadmin_email': superadmin.email if superadmin else None
        }
        
        # Rendre le template HTML
        html_message = render_to_string('emails/user_creation_email.html', context)
        
        # Liste des destinataires
        recipient_list = [user.email]
        cc_list = []
        if superadmin and superadmin.email != user.email:
            cc_list.append(superadmin.email)
        
        print(f"📬 Destinataire principal: {recipient_list}")
        print(f"📬 CC: {cc_list}")
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=f'Test CC Email - {entreprise.nom}',
            body=f'Bonjour {user.first_name},\n\nCeci est un test de la fonctionnalité CC email.\n\nCordialement,\nL\'équipe StoRage',
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
            cc=cc_list
        )
        email.attach_alternative(html_message, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        print(f"✅ Email envoyé avec succès!")
        print(f"   📤 Expéditeur: {settings.EMAIL_HOST_USER}")
        print(f"   📬 Destinataire: {user.email}")
        print(f"   📬 CC: {superadmin.email if superadmin else 'Aucun'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_email_template():
    """Test du template email."""
    print(f"\n📄 TEST TEMPLATE EMAIL")
    print("=" * 25)
    
    try:
        # Vérifier que le template existe
        template_path = 'emails/user_creation_email.html'
        
        # Essayer de rendre le template
        context = {
            'user': {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'},
            'entreprise': {'nom': 'Test Entreprise', 'id_entreprise': 'TEST123'},
            'boutique': {'nom': 'Test Boutique'},
            'temp_password': 'TempPass123!',
            'login_url': 'http://localhost:3000/connexion?entreprise_id=TEST123',
            'site_name': 'StoRage',
            'site_url': 'http://localhost:3000',
            'superadmin_email': 'admin@test.com'
        }
        
        html_content = render_to_string(template_path, context)
        
        print(f"✅ Template rendu avec succès!")
        print(f"   📄 Taille: {len(html_content)} caractères")
        print(f"   📧 Contient email utilisateur: {'test@example.com' in html_content}")
        print(f"   🏢 Contient nom entreprise: {'Test Entreprise' in html_content}")
        print(f"   🔑 Contient mot de passe: {'TempPass123!' in html_content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur template: {e}")
        return False

def test_email_configuration():
    """Test de la configuration email."""
    print(f"\n⚙️  TEST CONFIGURATION EMAIL")
    print("=" * 35)
    
    try:
        print(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"📧 EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'Non défini'}")
        print(f"📧 DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test de connexion SMTP
        import smtplib
        
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()
        
        print(f"✅ Configuration email valide!")
        print(f"✅ Connexion SMTP réussie!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def main():
    print("🚀 TEST FONCTIONNALITÉ CC EMAIL")
    print("=" * 40)
    
    # 1. Test de configuration email
    config_ok = test_email_configuration()
    
    # 2. Test du template email
    template_ok = test_email_template()
    
    # 3. Test de la fonctionnalité CC
    cc_ok = test_email_cc_functionality()
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ TESTS CC EMAIL")
    print("=" * 30)
    print(f"   ⚙️  Configuration email: {'✅' if config_ok else '❌'}")
    print(f"   📄 Template email: {'✅' if template_ok else '❌'}")
    print(f"   📧 Fonctionnalité CC: {'✅' if cc_ok else '❌'}")
    
    if config_ok and template_ok and cc_ok:
        print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
        print(f"   ✅ Configuration email fonctionnelle")
        print(f"   ✅ Template email valide")
        print(f"   ✅ Envoi avec CC opérationnel")
        print(f"\n📧 VÉRIFIEZ VOS EMAILS:")
        print(f"   📬 wilfriedtayouf7@gmail.com (destinataire principal)")
        print(f"   📬 admin@test.com (CC)")
    else:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS")
        if not config_ok:
            print(f"   - Vérifier la configuration email")
        if not template_ok:
            print(f"   - Vérifier le template email")
        if not cc_ok:
            print(f"   - Vérifier l'envoi avec CC")

if __name__ == "__main__":
    main()

























