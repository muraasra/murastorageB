"""
Permissions personnalisées pour gérer les limitations d'abonnement
"""
from rest_framework.permissions import BasePermission
from .subscription_utils import check_limit, check_feature

class HasSubscriptionLimit(BasePermission):
    """
    Permission qui vérifie si l'entreprise n'a pas atteint sa limite
    pour un type de ressource spécifique
    """
    resource_type = None  # À définir dans les sous-classes
    
    def has_permission(self, request, view):
        # Autoriser les requêtes GET, HEAD, OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Pour les autres méthodes (POST, PUT, PATCH, DELETE), vérifier les limites
        if request.method == 'POST' and self.resource_type:
            user = request.user
            if user.is_authenticated and user.entreprise:
                can_create, message = check_limit(user.entreprise, self.resource_type)
                if not can_create:
                    self.message = message
                    return False
        
        return True

class CanCreateUser(HasSubscriptionLimit):
    """Permission pour créer des utilisateurs"""
    resource_type = 'users'
    message = "Limite d'utilisateurs atteinte"

class CanCreateBoutique(HasSubscriptionLimit):
    """Permission pour créer des boutiques"""
    resource_type = 'boutiques'
    message = "Limite de boutiques atteinte"

class CanCreateProduit(HasSubscriptionLimit):
    """Permission pour créer des produits"""
    resource_type = 'produits'
    message = "Limite de produits atteinte"

class CanCreateFacture(HasSubscriptionLimit):
    """Permission pour créer des factures"""
    resource_type = 'factures'
    message = "Limite de factures mensuelles atteinte"

class HasFeatureAccess(BasePermission):
    """
    Permission qui vérifie si une fonctionnalité est disponible
    pour l'abonnement de l'entreprise
    """
    feature_name = None  # À définir dans les sous-classes
    
    def has_permission(self, request, view):
        if not self.feature_name:
            return True
        
        user = request.user
        if user.is_authenticated and user.entreprise:
            is_available, message = check_feature(user.entreprise, self.feature_name)
            if not is_available:
                self.message = message
                return False
        
        return True

class CanExportCSV(HasFeatureAccess):
    """Permission pour exporter en CSV"""
    feature_name = 'export_csv'
    message = "L'export CSV n'est pas disponible dans votre plan"

class CanExportExcel(HasFeatureAccess):
    """Permission pour exporter en Excel"""
    feature_name = 'export_excel'
    message = "L'export Excel n'est pas disponible dans votre plan"

class CanImportCSV(HasFeatureAccess):
    """Permission pour importer des CSV"""
    feature_name = 'import_csv'
    message = "L'import CSV n'est pas disponible dans votre plan"

class CanAccessAPI(HasFeatureAccess):
    """Permission pour accéder à l'API"""
    feature_name = 'api_access'
    message = "L'accès API n'est pas disponible dans votre plan"

class CanUseAdvancedAnalytics(HasFeatureAccess):
    """Permission pour utiliser les analyses avancées"""
    feature_name = 'advanced_analytics'
    message = "Les analyses avancées ne sont pas disponibles dans votre plan"











