"""
Views pour gérer les abonnements et limitations
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SubscriptionPlan, EntrepriseSubscription, UsageTracking
from .subscription_serializers import (
    SubscriptionPlanSerializer,
    EntrepriseSubscriptionSerializer,
    UsageTrackingSerializer,
    SubscriptionLimitsSerializer,
    CurrentUsageSerializer
)
from .subscription_utils import (
    get_entreprise_subscription,
    get_subscription_limits,
    get_current_usage,
    check_limit,
    check_feature
)
from .subscription_notifications import (
    process_subscription_change,
    check_and_send_limit_warnings,
    check_and_send_trial_warnings,
    check_and_send_subscription_expiry_warnings
)
from .permissions import IsAdminOrSuperAdmin

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour lister les plans d'abonnement disponibles
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """Comparer tous les plans disponibles"""
        plans = self.get_queryset()
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)

class EntrepriseSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les abonnements d'entreprise
    """
    queryset = EntrepriseSubscription.objects.all()
    serializer_class = EntrepriseSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer par entreprise de l'utilisateur"""
        user = self.request.user
        if user.role == 'superadmin' and user.entreprise:
            return EntrepriseSubscription.objects.filter(entreprise=user.entreprise)
        return EntrepriseSubscription.objects.none()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Récupérer l'abonnement actuel de l'entreprise"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = get_entreprise_subscription(request.user.entreprise)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def limits(self, request):
        """Récupérer les limites de l'abonnement actuel"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        limits = get_subscription_limits(request.user.entreprise)
        serializer = SubscriptionLimitsSerializer(data=limits)
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Récupérer l'utilisation actuelle de l'entreprise"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        usage = get_current_usage(request.user.entreprise)
        serializer = CurrentUsageSerializer(data=usage)
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Mettre à niveau l'abonnement"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'ID du plan requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = process_subscription_change(
            request.user.entreprise, 
            plan_id, 
            'upgrade'
        )
        
        if success:
            return Response({
                'success': True,
                'message': message
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def downgrade(self, request):
        """Rétrograder l'abonnement"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'ID du plan requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = process_subscription_change(
            request.user.entreprise, 
            plan_id, 
            'downgrade'
        )
        
        if success:
            return Response({
                'success': True,
                'message': message
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_limit(self, request):
        """Vérifier si une limite est atteinte"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resource_type = request.data.get('resource_type')
        if not resource_type:
            return Response({
                'error': 'Type de ressource requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        can_create, message = check_limit(request.user.entreprise, resource_type)
        
        return Response({
            'can_create': can_create,
            'message': message,
            'resource_type': resource_type
        })
    
    @action(detail=False, methods=['post'])
    def check_feature(self, request):
        """Vérifier si une fonctionnalité est disponible"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        feature_name = request.data.get('feature_name')
        if not feature_name:
            return Response({
                'error': 'Nom de la fonctionnalité requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_available, message = check_feature(request.user.entreprise, feature_name)
        
        return Response({
            'is_available': is_available,
            'message': message,
            'feature_name': feature_name
        })
    
    @action(detail=False, methods=['post'])
    def send_notifications(self, request):
        """Envoyer les notifications de vérification"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notifications_sent = []
        
        # Vérifier les limites
        if check_and_send_limit_warnings(request.user.entreprise):
            notifications_sent.append('limit_warnings')
        
        # Vérifier la période d'essai
        if check_and_send_trial_warnings(request.user.entreprise):
            notifications_sent.append('trial_warnings')
        
        # Vérifier l'expiration
        if check_and_send_subscription_expiry_warnings(request.user.entreprise):
            notifications_sent.append('expiry_warnings')
        
        return Response({
            'success': True,
            'notifications_sent': notifications_sent,
            'message': f'{len(notifications_sent)} type(s) de notifications envoyées'
        })

class UsageTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter le suivi d'utilisation
    """
    queryset = UsageTracking.objects.all()
    serializer_class = UsageTrackingSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filtrer par entreprise de l'utilisateur"""
        user = self.request.user
        if user.entreprise:
            return UsageTracking.objects.filter(entreprise=user.entreprise).order_by('-current_month')
        return UsageTracking.objects.none()

class EntrepriseSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les abonnements d'entreprise
    """
    queryset = EntrepriseSubscription.objects.all()
    serializer_class = EntrepriseSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer par entreprise de l'utilisateur"""
        user = self.request.user
        if user.role == 'superadmin' and user.entreprise:
            return EntrepriseSubscription.objects.filter(entreprise=user.entreprise)
        return EntrepriseSubscription.objects.none()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Récupérer l'abonnement actuel de l'entreprise"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = get_entreprise_subscription(request.user.entreprise)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def limits(self, request):
        """Récupérer les limites de l'abonnement actuel"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        limits = get_subscription_limits(request.user.entreprise)
        serializer = SubscriptionLimitsSerializer(data=limits)
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Récupérer l'utilisation actuelle de l'entreprise"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        usage = get_current_usage(request.user.entreprise)
        serializer = CurrentUsageSerializer(data=usage)
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Mettre à niveau l'abonnement"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'ID du plan requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({
                'error': 'Plan invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = get_entreprise_subscription(request.user.entreprise)
        old_plan = subscription.plan
        
        subscription.plan = new_plan
        subscription.save()
        
        return Response({
            'success': True,
            'message': f'Abonnement mis à niveau de {old_plan.display_name} vers {new_plan.display_name}',
            'subscription': EntrepriseSubscriptionSerializer(subscription).data
        })
    
    @action(detail=False, methods=['post'])
    def check_limit(self, request):
        """Vérifier si une limite est atteinte"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resource_type = request.data.get('resource_type')
        if not resource_type:
            return Response({
                'error': 'Type de ressource requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        can_create, message = check_limit(request.user.entreprise, resource_type)
        
        return Response({
            'can_create': can_create,
            'message': message,
            'resource_type': resource_type
        })
    
    @action(detail=False, methods=['post'])
    def check_feature(self, request):
        """Vérifier si une fonctionnalité est disponible"""
        if not request.user.entreprise:
            return Response({
                'error': 'Aucune entreprise associée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        feature_name = request.data.get('feature_name')
        if not feature_name:
            return Response({
                'error': 'Nom de la fonctionnalité requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_available, message = check_feature(request.user.entreprise, feature_name)
        
        return Response({
            'is_available': is_available,
            'message': message,
            'feature_name': feature_name
        })

class UsageTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter le suivi d'utilisation
    """
    queryset = UsageTracking.objects.all()
    serializer_class = UsageTrackingSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filtrer par entreprise de l'utilisateur"""
        user = self.request.user
        if user.entreprise:
            return UsageTracking.objects.filter(entreprise=user.entreprise).order_by('-current_month')
        return UsageTracking.objects.none()

