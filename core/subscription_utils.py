"""
Utilitaires pour gérer les limitations d'abonnement
"""
from django.utils import timezone
from .models import SubscriptionPlan, EntrepriseSubscription, UsageTracking, Entreprise, User, Boutique, Produit, Facture
from datetime import datetime, timedelta

def get_entreprise_subscription(entreprise):
    """Récupérer l'abonnement d'une entreprise"""
    try:
        return EntrepriseSubscription.objects.select_related('plan').get(entreprise=entreprise)
    except EntrepriseSubscription.DoesNotExist:
        # Si pas d'abonnement, créer un abonnement FREE par défaut
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name='free',
            defaults={
                'display_name': 'Free',
                'description': 'Plan gratuit avec limitations',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_entreprises': 1,
                'max_boutiques': 1,
                'max_users': 2,
                'max_produits': 50,
                'max_factures_per_month': 100,
                'allow_export_csv': False,
                'allow_export_excel': False,
                'allow_import_csv': False,
                'allow_api_access': False,
                'allow_multiple_entreprises': False,
                'allow_advanced_analytics': False,
                'allow_custom_branding': False,
                'support_level': 'email',
            }
        )
        
        # Créer l'abonnement avec période d'essai de 14 jours
        subscription = EntrepriseSubscription.objects.create(
            entreprise=entreprise,
            plan=free_plan,
            status='active',
            trial_end_date=timezone.now() + timedelta(days=14)
        )
        return subscription

def get_or_create_usage_tracking(entreprise):
    """Récupérer ou créer le suivi d'utilisation pour une entreprise"""
    current_month = timezone.now().date().replace(day=1)
    
    usage, created = UsageTracking.objects.get_or_create(
        entreprise=entreprise,
        current_month=current_month,
        defaults={
            'factures_count': 0,
            'produits_count': 0,
            'users_count': 0,
            'boutiques_count': 0,
        }
    )
    
    # Mettre à jour les compteurs actuels (même si l'objet vient d'être créé)
    usage.users_count = User.objects.filter(entreprise=entreprise).count()
    usage.boutiques_count = Boutique.objects.filter(entreprise=entreprise).count()
    usage.produits_count = Produit.objects.filter(entreprise=entreprise).count()
    
    # Compter les factures du mois en cours (via la boutique liée à l'entreprise)
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage.factures_count = Facture.objects.filter(
        boutique__entreprise=entreprise,
        created_at__gte=start_of_month
    ).count()
    
    usage.save()
    
    return usage

def check_limit(entreprise, resource_type):
    """
    Vérifier si une entreprise a atteint sa limite pour un type de ressource
    
    Args:
        entreprise: Instance de l'entreprise
        resource_type: Type de ressource ('users', 'boutiques', 'produits', 'factures')
    
    Returns:
        tuple: (can_create: bool, message: str)
    """
    subscription = get_entreprise_subscription(entreprise)
    usage = get_or_create_usage_tracking(entreprise)
    plan = subscription.plan
    
    if resource_type == 'users':
        current = usage.users_count
        limit = plan.max_users
        if limit and current >= limit:
            return False, f"Limite d'utilisateurs atteinte ({current}/{limit}). Passez à un plan supérieur."
    
    elif resource_type == 'boutiques':
        current = usage.boutiques_count
        limit = plan.max_boutiques
        if limit and current >= limit:
            return False, f"Limite de boutiques atteinte ({current}/{limit}). Passez à un plan supérieur."
    
    elif resource_type == 'produits':
        current = usage.produits_count
        limit = plan.max_produits
        if limit and current >= limit:
            return False, f"Limite de produits atteinte ({current}/{limit}). Passez à un plan supérieur."
    
    elif resource_type == 'factures':
        current = usage.factures_count
        limit = plan.max_factures_per_month
        if limit and current >= limit:
            return False, f"Limite de factures mensuelles atteinte ({current}/{limit}). Passez à un plan supérieur."
    
    return True, "OK"

def check_feature(entreprise, feature_name):
    """
    Vérifier si une fonctionnalité est disponible pour une entreprise
    
    Args:
        entreprise: Instance de l'entreprise
        feature_name: Nom de la fonctionnalité
    
    Returns:
        tuple: (is_available: bool, message: str)
    """
    subscription = get_entreprise_subscription(entreprise)
    plan = subscription.plan
    
    feature_map = {
        'export_csv': plan.allow_export_csv,
        'export_excel': plan.allow_export_excel,
        'import_csv': plan.allow_import_csv,
        'api_access': plan.allow_api_access,
        'multiple_entreprises': plan.allow_multiple_entreprises,
        'advanced_analytics': plan.allow_advanced_analytics,
        'custom_branding': plan.allow_custom_branding,
    }
    
    if feature_name not in feature_map:
        return False, f"Fonctionnalité inconnue: {feature_name}"
    
    if not feature_map[feature_name]:
        return False, f"Cette fonctionnalité n'est pas disponible dans votre plan {plan.display_name}. Passez à un plan supérieur."
    
    return True, "OK"

def get_subscription_limits(entreprise):
    """Récupérer toutes les limites pour une entreprise"""
    subscription = get_entreprise_subscription(entreprise)
    plan = subscription.plan
    
    return {
        'plan_name': plan.name,
        'display_name': plan.display_name,
        'max_entreprises': plan.max_entreprises,
        'max_boutiques': plan.max_boutiques,
        'max_users': plan.max_users,
        'max_produits': plan.max_produits,
        'max_factures_per_month': plan.max_factures_per_month,
        'allow_export_csv': plan.allow_export_csv,
        'allow_export_excel': plan.allow_export_excel,
        'allow_import_csv': plan.allow_import_csv,
        'allow_api_access': plan.allow_api_access,
        'allow_multiple_entreprises': plan.allow_multiple_entreprises,
        'allow_advanced_analytics': plan.allow_advanced_analytics,
        'allow_custom_branding': plan.allow_custom_branding,
        'support_level': plan.support_level,
        'price_monthly': plan.price_monthly,
        'price_yearly': plan.price_yearly,
    }

def get_current_usage(entreprise):
    """Récupérer l'utilisation actuelle d'une entreprise"""
    usage = get_or_create_usage_tracking(entreprise)
    subscription = get_entreprise_subscription(entreprise)
    plan = subscription.plan
    
    return {
        'factures_count': usage.factures_count,
        'produits_count': usage.produits_count,
        'users_count': usage.users_count,
        'boutiques_count': usage.boutiques_count,
        'factures_limit': plan.max_factures_per_month,
        'produits_limit': plan.max_produits,
        'users_limit': plan.max_users,
        'boutiques_limit': plan.max_boutiques,
        'is_factures_limit_reached': plan.max_factures_per_month and usage.factures_count >= plan.max_factures_per_month,
        'is_produits_limit_reached': plan.max_produits and usage.produits_count >= plan.max_produits,
        'is_users_limit_reached': usage.users_count >= plan.max_users,
        'is_boutiques_limit_reached': usage.boutiques_count >= plan.max_boutiques,
    }

def increment_usage(entreprise, resource_type):
    """Incrémenter le compteur d'utilisation pour un type de ressource"""
    usage = get_or_create_usage_tracking(entreprise)
    
    if resource_type == 'factures':
        usage.increment_facture_count()
    elif resource_type == 'produits':
        usage.increment_produit_count()
    elif resource_type == 'users':
        count = User.objects.filter(entreprise=entreprise).count()
        usage.update_users_count(count)
    elif resource_type == 'boutiques':
        count = Boutique.objects.filter(entreprise=entreprise).count()
        usage.update_boutiques_count(count)







