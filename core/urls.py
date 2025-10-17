from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import *
from .subscription_views import SubscriptionPlanViewSet, EntrepriseSubscriptionViewSet, UsageTrackingViewSet
from django.contrib import admin
from django.urls import path,include

router = DefaultRouter()
# Nouvelles routes pour les entreprises
router.register(r'inscription', InscriptionEntrepriseViewSet, basename='inscription')
router.register(r'entreprises', EntrepriseViewSet)
router.register(r'email-verification', EmailVerificationViewSet, basename='email-verification')
router.register(r'boutiques', BoutiqueViewSet)
router.register(r'produits', ProduitViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'fournisseurs', FournisseurViewSet)
router.register(r'stocks', StockViewSet)
router.register(r'mouvements-stock', MouvementStockViewSet)
router.register(r'prix-produits', PrixProduitViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'partenaires', PartenaireViewSet)
router.register(r'factures', FactureViewSet)
router.register(r'commandes-client', CommandeClientViewSet)
router.register(r'commandes-partenaire', CommandePartenaireViewSet)
router.register(r'versements', VersementViewSet)
router.register(r'historiques-stock', HistoriqueStockViewSet)
router.register(r'journaux', JournalViewSet)
router.register(r'users', UserViewSet)
# Routes pour les abonnements
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plans')
router.register(r'subscriptions', EntrepriseSubscriptionViewSet, basename='subscriptions')
router.register(r'usage-tracking', UsageTrackingViewSet, basename='usage-tracking')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomAuthTokenView.as_view(), name='api_token_auth'),
    path('auth/jwt/login/', CustomJWTTokenObtainPairView.as_view(), name='api_jwt_auth'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='api_jwt_refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='api_jwt_verify'),
    path('contact/submit/', contact_form_submit, name='contact_form_submit'),
]