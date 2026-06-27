"""
Views pour les paiements et l'administration plateforme.
"""
import datetime
from rest_framework import viewsets, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum

from .models import (
    PaymentTransaction, SubscriptionPlan, EntrepriseSubscription,
    Entreprise, User
)
from .subscription_utils import get_entreprise_subscription
from .permissions import IsAdminOrSuperAdmin
from .pagination import StandardPagination


# ─── Serializers inline ───────────────────────────────────────────────────────

class PaymentTransactionSerializer(drf_serializers.ModelSerializer):
    plan_name = drf_serializers.CharField(source='plan.display_name', read_only=True)
    entreprise_nom = drf_serializers.CharField(source='entreprise.nom', read_only=True)
    method_label = drf_serializers.CharField(source='get_method_display', read_only=True)
    status_label = drf_serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'entreprise', 'entreprise_nom', 'plan', 'plan_name',
            'amount', 'currency', 'method', 'method_label',
            'status', 'status_label', 'billing_period',
            'phone_number', 'card_last4', 'external_reference',
            'failure_reason', 'notes', 'created_at', 'paid_at',
        ]
        read_only_fields = ['id', 'created_at', 'paid_at']


# ─── Payment ViewSet ──────────────────────────────────────────────────────────

class PaymentViewSet(viewsets.GenericViewSet):
    """Gestion des paiements d'abonnement."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer

    def get_queryset(self):
        user = self.request.user
        qs = PaymentTransaction.objects.select_related('entreprise', 'plan').order_by('-created_at')
        if user.is_staff or user.is_superuser:
            return qs
        if user.entreprise:
            return qs.filter(entreprise=user.entreprise)
        return PaymentTransaction.objects.none()

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initier un paiement (simulation — les vraies API seront branchées plus tard)."""
        if not request.user.entreprise:
            return Response({'error': 'Aucune entreprise associée'}, status=status.HTTP_400_BAD_REQUEST)

        plan_id = request.data.get('plan_id')
        method = request.data.get('method')
        billing_period = request.data.get('billing_period', 'monthly')
        phone_number = request.data.get('phone_number', '')
        card_last4 = request.data.get('card_last4', '')

        if not plan_id or not method:
            return Response({'error': 'plan_id et method sont requis'}, status=status.HTTP_400_BAD_REQUEST)

        VALID_METHODS = ['orange_money', 'mtn_money', 'stripe', 'bank_card']
        if method not in VALID_METHODS:
            return Response(
                {'error': f'Methode invalide. Valeurs: {VALID_METHODS}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan introuvable'}, status=status.HTTP_404_NOT_FOUND)

        amount = plan.price_yearly if billing_period == 'yearly' else plan.price_monthly

        sub = get_entreprise_subscription(request.user.entreprise)

        transaction = PaymentTransaction.objects.create(
            entreprise=request.user.entreprise,
            subscription=sub,
            plan=plan,
            amount=amount,
            method=method,
            billing_period=billing_period,
            status='processing',
            phone_number=phone_number,
            card_last4=card_last4,
            initiated_by=request.user,
        )

        # SIMULATION : validation immédiate
        transaction.status = 'success'
        transaction.paid_at = timezone.now()
        transaction.save()

        # Appliquer le changement d'abonnement
        sub.plan = plan
        sub.status = 'active'
        sub.billing_period = billing_period
        sub.payment_method = method
        sub.last_payment_date = timezone.now()
        if billing_period == 'yearly':
            sub.end_date = timezone.now() + datetime.timedelta(days=365)
            sub.next_payment_date = timezone.now() + datetime.timedelta(days=365)
        else:
            sub.end_date = timezone.now() + datetime.timedelta(days=30)
            sub.next_payment_date = timezone.now() + datetime.timedelta(days=30)
        sub.trial_end_date = None
        sub.save()

        return Response({
            'success': True,
            'transaction_id': transaction.id,
            'status': 'success',
            'message': f'Paiement de {int(amount):,} FCFA valide. Abonnement {plan.display_name} actif.',
            'plan': plan.display_name,
            'amount': int(amount),
            'method': method,
            'paid_at': transaction.paid_at.isoformat(),
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Historique des paiements de l'entreprise connectée."""
        qs = self.get_queryset()[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ─── Platform Admin ViewSet ───────────────────────────────────────────────────

class PlatformAdminViewSet(viewsets.ViewSet):
    """
    Endpoints reserves a l administrateur de la plateforme MuraStorage.
    Necessite is_staff=True ou is_superuser=True.
    """
    permission_classes = [IsAuthenticated]

    def _assert_platform_admin(self, user):
        if not (user.is_staff or user.is_superuser):
            raise drf_serializers.ValidationError({'error': 'Acces reserve a l administrateur plateforme'})

    @action(detail=False, methods=['get'])
    def entreprises(self, request):
        """Lister toutes les entreprises avec leur abonnement."""
        self._assert_platform_admin(request.user)

        entreprises = Entreprise.objects.prefetch_related('subscription__plan').order_by('-created_at')
        paginator = StandardPagination()
        page = paginator.paginate_queryset(entreprises, request)

        data = []
        for e in (page or entreprises):
            try:
                sub = e.subscription
                sub_data = {
                    'plan': sub.plan.display_name,
                    'plan_name': sub.plan.name,
                    'status': sub.status,
                    'end_date': sub.end_date,
                    'trial_end_date': sub.trial_end_date,
                    'billing_period': sub.billing_period,
                    'auto_renew': sub.auto_renew,
                }
            except Exception:
                sub_data = {'plan': 'Aucun', 'plan_name': 'none', 'status': 'none'}

            data.append({
                'id': e.id,
                'id_entreprise': e.id_entreprise,
                'nom': e.nom,
                'email': e.email,
                'ville': e.ville,
                'is_active': e.is_active,
                'created_at': e.created_at,
                'subscription': sub_data,
                'users_count': User.objects.filter(entreprise=e).count(),
            })

        if page is not None:
            return paginator.get_paginated_response(data)
        return Response(data)

    @action(detail=False, methods=['post'])
    def set_subscription(self, request):
        """Modifier manuellement l abonnement d une entreprise."""
        self._assert_platform_admin(request.user)

        entreprise_id = request.data.get('entreprise_id')
        plan_name = request.data.get('plan_name')
        status_val = request.data.get('status', 'active')
        days = int(request.data.get('days', 30))
        notes = request.data.get('notes', '')

        try:
            entreprise = Entreprise.objects.get(id=entreprise_id)
        except Entreprise.DoesNotExist:
            return Response({'error': 'Entreprise introuvable'}, status=status.HTTP_404_NOT_FOUND)

        try:
            plan = SubscriptionPlan.objects.get(name=plan_name, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan introuvable'}, status=status.HTTP_404_NOT_FOUND)

        sub, _ = EntrepriseSubscription.objects.get_or_create(
            entreprise=entreprise, defaults={'plan': plan}
        )
        sub.plan = plan
        sub.status = status_val
        sub.end_date = timezone.now() + datetime.timedelta(days=days)
        sub.trial_end_date = None
        sub.save()

        PaymentTransaction.objects.create(
            entreprise=entreprise,
            subscription=sub,
            plan=plan,
            amount=0,
            method='manual',
            billing_period='monthly',
            status='success',
            initiated_by=request.user,
            notes=notes,
            paid_at=timezone.now(),
        )

        return Response({
            'success': True,
            'message': f'Abonnement de {entreprise.nom} mis a jour: {plan.display_name} ({days} jours)',
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques globales de la plateforme."""
        self._assert_platform_admin(request.user)

        total = Entreprise.objects.count()
        active = Entreprise.objects.filter(is_active=True).count()

        plans_dist = {}
        for sub in EntrepriseSubscription.objects.select_related('plan').all():
            k = sub.plan.display_name
            plans_dist[k] = plans_dist.get(k, 0) + 1

        revenue = PaymentTransaction.objects.filter(
            status='success',
            method__in=['orange_money', 'mtn_money', 'stripe', 'bank_card'],
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'total_entreprises': total,
            'active_entreprises': active,
            'inactive_entreprises': total - active,
            'plans_distribution': plans_dist,
            'total_revenue_simulated': int(revenue),
        })

    @action(detail=False, methods=['post'])
    def toggle_entreprise(self, request):
        """Activer / desactiver une entreprise."""
        self._assert_platform_admin(request.user)
        entreprise_id = request.data.get('entreprise_id')
        try:
            e = Entreprise.objects.get(id=entreprise_id)
        except Entreprise.DoesNotExist:
            return Response({'error': 'Entreprise introuvable'}, status=status.HTTP_404_NOT_FOUND)
        e.is_active = not e.is_active
        e.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': e.is_active, 'entreprise': e.nom})
