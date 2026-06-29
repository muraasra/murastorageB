from django.db import models as django_models
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from django.db.models.functions import TruncDate
from .serializers import *
from django.db import transaction
from rest_framework import serializers
from .permissions import *
from .subscription_permissions import (
    CanCreateUser,
    CanCreateBoutique,
    CanCreateProduit,
    CanCreateFacture,
    CanExportCSV,
    CanExportExcel,
    CanImportCSV,
)
from .cache_utils import cache_api_response, CacheManager
from .pagination import OptimizedPageNumberPagination, SmartPagination
from .password_reset import PasswordResetManager
from django.db import transaction
import secrets
import string

# Vue d'authentification JWT personnalisée
class CustomJWTTokenObtainPairView(TokenObtainPairView):
    """Vue d'authentification JWT personnalisée qui retourne le maximum d'informations"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                # Identifier l'utilisateur depuis les données de connexion
                email_or_username = request.data.get('email') or request.data.get('username', '')
                from django.contrib.auth import get_user_model
                UserModel = get_user_model()
                user = None
                if '@' in str(email_or_username):
                    user = UserModel.objects.filter(email=email_or_username).first()
                else:
                    user = UserModel.objects.filter(username=email_or_username).first()
                if user:
                    boutique = getattr(user, 'boutique', None)
                    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
                    if ip and ',' in ip:
                        ip = ip.split(',')[0].strip()
                    Journal.objects.create(
                        utilisateur=user,
                        entreprise=getattr(boutique, 'entreprise', None) if boutique else None,
                        boutique=boutique,
                        type_operation='connexion',
                        description=f"{user.get_full_name() or user.username} s'est connecté(e)",
                        ip_address=ip or None,
                    )
            except Exception:
                pass
        return response

# Serializer pour l'authentification Token avec support email
class EmailAuthTokenSerializer(serializers.Serializer):
    """Serializer qui permet l'authentification par email ou username"""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not username and not email:
            raise serializers.ValidationError('Username ou email requis')

        # Si email est fourni, trouver l'utilisateur par email
        if email:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError('Aucun utilisateur trouvé avec cet email')
        else:
            username = username

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Compte utilisateur désactivé')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Identifiants incorrects')
        else:
            raise serializers.ValidationError('Username et mot de passe requis')

# Vue d'authentification Token (legacy)
class CustomAuthTokenView(ObtainAuthToken):
    """Vue d'authentification Token (legacy) qui retourne plus d'informations et supporte l'email"""
    serializer_class = EmailAuthTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'entreprise_id': user.entreprise.id_entreprise if user.entreprise else None,
            'entreprise_nom': user.entreprise.nom if user.entreprise else None,
            'boutique_id': user.boutique.id if user.boutique else None,
            'boutique_nom': user.boutique.nom if user.boutique else None,
        })

# Vue pour l'inscription d'entreprise (création uniquement — pas de list/retrieve/update/delete publics)
class InscriptionEntrepriseViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet pour l'inscription d'entreprise — POST uniquement, sans authentification."""
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseCreateSerializer
    permission_classes = [AllowAny]

# Vue personnalisée pour la création d'utilisateurs avec envoi d'email
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les utilisateurs avec envoi d'email automatique"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'entreprise', 'boutique', 'is_active_employee']
    search_fields = ['first_name', 'last_name', 'email', 'username']
    ordering_fields = ['date_joined', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        """Filtrer les utilisateurs par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user

        # Platform admin (superadmin sans entreprise) : voit tout
        if user.role == 'superadmin' and not user.entreprise:
            return queryset.select_related('entreprise', 'boutique')

        # Tous les autres : uniquement leur entreprise
        if user.entreprise:
            queryset = queryset.filter(entreprise=user.entreprise)
        else:
            queryset = queryset.filter(id=user.id)

        return queryset.select_related('entreprise', 'boutique')

    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Bloquer la création si limite atteinte
            if self.action == 'create':
                permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin, CanCreateUser]
            else:
                permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        """Mettre à jour un utilisateur avec protection du rôle superadmin"""
        instance = self.get_object()
        
        # Protection : empêcher la modification du rôle superadmin
        if instance.role == 'superadmin' and 'role' in request.data:
            if request.data['role'] != 'superadmin':
                return Response({
                    'error': 'Le rôle Super Admin ne peut pas être modifié'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Protection : empêcher la création d'un nouveau superadmin
        if 'role' in request.data and request.data['role'] == 'superadmin':
            if instance.role != 'superadmin':
                return Response({
                    'error': 'Impossible de promouvoir un utilisateur au rôle Super Admin'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un utilisateur avec envoi d'email automatique"""
        # Protection : empêcher la création d'utilisateurs avec le rôle superadmin
        if 'role' in request.data and request.data['role'] == 'superadmin':
            return Response({
                'error': 'Impossible de créer un utilisateur avec le rôle Super Admin'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Générer un mot de passe temporaire
        temp_password = self.generate_temp_password()
        
        # Créer l'utilisateur avec l'entreprise de l'utilisateur connecté
        user_data = serializer.validated_data.copy()
        if not user_data.get('entreprise') and request.user.entreprise:
            user_data['entreprise'] = request.user.entreprise
        
        user = serializer.save(**user_data)
        user.set_password(temp_password)
        user.save()
        
        # Envoyer l'email si demandé
        send_email = request.data.get('send_email', False)
        if send_email:
            self.send_user_creation_email(user, temp_password)
        
        # Retourner la réponse sans le mot de passe
        response_serializer = self.get_serializer(user)
        return Response({
            'user': response_serializer.data,
            'temp_password': temp_password if not send_email else None,
            'email_sent': send_email,
            'message': 'Utilisateur créé avec succès'
        }, status=status.HTTP_201_CREATED)

    def generate_temp_password(self):
        """Générer un mot de passe temporaire sécurisé"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        return password

    def send_user_creation_email(self, user, temp_password):
        """Envoyer un email de création d'utilisateur avec le SuperAdmin en CC"""
        try:
            # Récupérer les informations de l'entreprise
            entreprise = user.entreprise
            boutique = user.boutique
            
            # Récupérer l'email du SuperAdmin de l'entreprise
            superadmin_email = None
            try:
                superadmin = User.objects.filter(entreprise=entreprise, role='superadmin').first()
                if superadmin:
                    superadmin_email = superadmin.email
            except Exception as e:
                print(f"Erreur récupération SuperAdmin: {e}")
            
            # Construire l'URL de connexion avec l'ID entreprise
            login_url = f"{settings.FRONTEND_URL}/connexion?entreprise_id={entreprise.id_entreprise}"
            
            # Contexte pour le template
            context = {
                'user': user,
                'entreprise': entreprise,
                'boutique': boutique,
                'temp_password': temp_password,
                'login_url': login_url,
                'site_name': 'StoRage',
                'site_url': settings.FRONTEND_URL,
                'superadmin_email': superadmin_email
            }
            
            # Rendre le template HTML
            html_message = render_to_string('emails/user_creation_email.html', context)
            
            # Liste des destinataires (utilisateur + SuperAdmin en CC)
            recipient_list = [user.email]
            cc_list = []
            if superadmin_email and superadmin_email != user.email:
                cc_list.append(superadmin_email)
            
            # Envoyer l'email avec CC
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=f'Bienvenue sur StoRage - {entreprise.nom}',
                body=f'Bonjour {user.first_name},\n\nVotre compte a été créé avec succès.\n\nIdentifiants de connexion:\nEmail: {user.email}\nMot de passe temporaire: {temp_password}\n\nLien de connexion: {login_url}\n\nCordialement,\nL\'équipe StoRage',
                from_email=settings.EMAIL_HOST_USER,
                to=recipient_list,
                cc=cc_list
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            
            print(f"Email envoyé à {user.email} avec CC à {cc_list}")
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            # Ne pas faire échouer la création d'utilisateur si l'email échoue
    
    def perform_create(self, serializer):
        user = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('users')
        except Exception as e:
            print(f"Erreur invalidation cache users create: {e}")
        return user

    def perform_update(self, serializer):
        user = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('users')
        except Exception as e:
            print(f"Erreur invalidation cache users update: {e}")
        return user

    def perform_destroy(self, instance):
        instance.delete()
        try:
            CacheManager.invalidate_api_prefix('users')
        except Exception as e:
            print(f"Erreur invalidation cache users destroy: {e}")
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def inscription(self, request):
        """Endpoint pour l'inscription d'une nouvelle entreprise
        
        Crée une nouvelle entreprise avec un utilisateur SuperAdmin.
        Envoie automatiquement un email de vérification.
        """
        try:
            # Valider et créer directement avec le serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            entreprise = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Entreprise créée avec succès. Un email de vérification a été envoyé.',
                'entreprise': EntrepriseSerializer(entreprise).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erreur lors de la création: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

# Vue pour gérer les entreprises
class EntrepriseViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les entreprises"""
    queryset = Entreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'secteur_activite', 'ville']
    ordering_fields = ['nom', 'created_at']
    
    def get_queryset(self):
        """Filtrer les entreprises selon le rôle de l'utilisateur"""
        user = self.request.user
        # Platform admin (superadmin sans entreprise) : voit toutes les entreprises
        if user.role == 'superadmin' and not user.entreprise:
            return Entreprise.objects.all()
        # Tous les autres : uniquement leur propre entreprise
        if user.entreprise:
            return Entreprise.objects.filter(id=user.entreprise.id)
        return Entreprise.objects.none()
    
    @action(detail=True, methods=['get'])
    def boutiques(self, request, pk=None):
        """Récupérer les boutiques d'une entreprise"""
        entreprise = self.get_object()
        boutiques = entreprise.boutiques.all()
        serializer = BoutiqueSerializer(boutiques, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def utilisateurs(self, request, pk=None):
        """Récupérer les utilisateurs d'une entreprise"""
        entreprise = self.get_object()
        users = entreprise.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# Vue pour la vérification d'email
class EmailVerificationViewSet(viewsets.GenericViewSet):
    """ViewSet pour la vérification d'email — actions personnalisées uniquement, pas de list/retrieve publics."""
    queryset = EmailVerification.objects.none()
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_code(self, request):
        """Vérifier le code de vérification email"""
        from .utils import verify_email_code, send_confirmation_email
        
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({
                'success': False,
                'message': 'Email et code requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Trouver l'utilisateur par email
            user = User.objects.get(email=email)
            
            # Vérifier le code
            is_valid, message = verify_email_code(user, code)
            
            if is_valid:
                # Envoyer l'email de confirmation
                entreprise = user.entreprise
                boutique = user.boutique
                
                if entreprise and boutique:
                    send_confirmation_email(user, entreprise, boutique)
                
                return Response({
                    'success': True,
                    'message': 'Email vérifié avec succès ! Vous allez recevoir un email de confirmation.',
                    'user': UserSerializer(user).data,
                    'entreprise': EntrepriseSerializer(entreprise).data if entreprise else None
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Utilisateur non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erreur lors de la vérification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def resend_code(self, request):
        """Renvoyer le code de vérification"""
        from .utils import send_verification_email
        
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Trouver l'utilisateur par email
            user = User.objects.get(email=email)
            entreprise = user.entreprise
            
            if not entreprise:
                return Response({
                    'success': False,
                    'message': 'Entreprise non trouvée'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Renvoyer l'email de vérification
            email_sent, result = send_verification_email(user, entreprise)
            
            if email_sent:
                return Response({
                    'success': True,
                    'message': 'Code de vérification renvoyé avec succès'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Impossible d\'envoyer l\'email pour le moment. Veuillez réessayer dans quelques minutes ou contacter le support.',
                    'detail': str(result)
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Utilisateur non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erreur: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FactureFilter(django_filters.FilterSet):
    created_at  = django_filters.DateFilter(method='filter_by_date')
    date_debut  = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_fin    = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Facture
        fields = ['type', 'status', 'boutique', 'created_at', 'date_debut', 'date_fin', 'entreprise']

    def filter_by_date(self, queryset, name, value):
        return queryset.annotate(date_only=TruncDate('created_at')).filter(date_only=value)

# Boutique : uniquement superadmin peut y toucher
class BoutiqueViewSet(viewsets.ModelViewSet):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entreprise']
    search_fields = ['nom', 'ville']
    ordering_fields = ['nom']
    
    def get_queryset(self):
        """Filtrer les boutiques par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()

        user = self.request.user
        # Platform admin (superadmin sans entreprise) : voit tout, filtre optionnel
        if user.role == 'superadmin' and not user.entreprise:
            return queryset.select_related('entreprise')

        # Tous les autres : uniquement les boutiques de leur entreprise
        if user.entreprise:
            queryset = queryset.filter(entreprise=user.entreprise)
        else:
            queryset = queryset.none()

        return queryset.select_related('entreprise')

    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Bloquer la création si limite atteinte
            if self.action == 'create':
                permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin, CanCreateBoutique]
            else:
                permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('boutiques')
        except Exception as e:
            print(f"Erreur invalidation cache boutiques create: {e}")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('boutiques')
        except Exception as e:
            print(f"Erreur invalidation cache boutiques update: {e}")
        return instance

    def perform_destroy(self, instance):
        instance.delete()
        try:
            CacheManager.invalidate_api_prefix('boutiques')
        except Exception as e:
            print(f"Erreur invalidation cache boutiques destroy: {e}")

# Catégorie : gestion des catégories de produits
class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entreprise', 'actif', 'parent']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'created_at']
    
    def get_queryset(self):
        """Filtrer les catégories par entreprise de l'utilisateur connecté (tous rôles)."""
        queryset = super().get_queryset()
        if self.request.user.entreprise:
            queryset = queryset.filter(entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        return queryset.select_related('parent', 'entreprise')

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            if instance.entreprise_id:
                CacheManager.invalidate_produits_cache(instance.entreprise_id)
            CacheManager.invalidate_api_prefix('categories')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache categories create: {e}")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            if instance.entreprise_id:
                CacheManager.invalidate_produits_cache(instance.entreprise_id)
            CacheManager.invalidate_api_prefix('categories')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache categories update: {e}")
        return instance

    def perform_destroy(self, instance):
        entreprise_id = instance.entreprise_id
        instance.delete()
        try:
            if entreprise_id:
                CacheManager.invalidate_produits_cache(entreprise_id)
            CacheManager.invalidate_api_prefix('categories')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache categories destroy: {e}")

# Fournisseur : gestion des fournisseurs
class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entreprise', 'actif']
    search_fields = ['nom', 'code_fournisseur', 'email', 'telephone']
    ordering_fields = ['nom', 'created_at']
    
    def get_queryset(self):
        """Filtrer les fournisseurs par entreprise de l'utilisateur connecté (tous rôles)."""
        queryset = super().get_queryset()
        if self.request.user.entreprise:
            queryset = queryset.filter(entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        return queryset.select_related('entreprise')

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            if instance.entreprise_id:
                CacheManager.invalidate_produits_cache(instance.entreprise_id)
            CacheManager.invalidate_api_prefix('fournisseurs')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache fournisseurs create: {e}")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            if instance.entreprise_id:
                CacheManager.invalidate_produits_cache(instance.entreprise_id)
            CacheManager.invalidate_api_prefix('fournisseurs')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache fournisseurs update: {e}")
        return instance

    def perform_destroy(self, instance):
        entreprise_id = instance.entreprise_id
        instance.delete()
        try:
            if entreprise_id:
                CacheManager.invalidate_produits_cache(entreprise_id)
            CacheManager.invalidate_api_prefix('fournisseurs')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache fournisseurs destroy: {e}")

# Variantes produit : gestion des variantes (taille, couleur, etc.)
class ProduitVarianteViewSet(viewsets.ModelViewSet):
    queryset = ProduitVariante.objects.select_related('produit')
    serializer_class = ProduitVarianteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['produit', 'actif']
    search_fields = ['nom', 'sku', 'code_barres']
    ordering_fields = ['nom', 'prix_vente', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'superadmin' and not user.entreprise:
            return qs
        if user.entreprise:
            return qs.filter(produit__entreprise=user.entreprise)
        if user.boutique and user.boutique.entreprise:
            return qs.filter(produit__entreprise=user.boutique.entreprise)
        return qs.none()

# Stock : gestion des stocks par entrepôt
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['produit', 'entrepot', 'variante']
    search_fields = ['produit__nom', 'emplacement']
    ordering_fields = ['quantite', 'updated_at']

    def get_queryset(self):
        """Filtrer les stocks par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()

        if self.request.user.entreprise:
            queryset = queryset.filter(entrepot__entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()

        return queryset.select_related(
            'produit', 'entrepot', 'entrepot__entreprise', 'variante'
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        # Invalider caches liés
        try:
            if instance.entrepot_id:
                CacheManager.invalidate_stocks_cache(instance.entrepot_id)
                if instance.entrepot and instance.entrepot.entreprise_id:
                    CacheManager.invalidate_produits_cache(instance.entrepot.entreprise_id)
            CacheManager.invalidate_api_prefix('stocks')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache stocks create: {e}")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            if instance.entrepot_id:
                CacheManager.invalidate_stocks_cache(instance.entrepot_id)
                if instance.entrepot and instance.entrepot.entreprise_id:
                    CacheManager.invalidate_produits_cache(instance.entrepot.entreprise_id)
            CacheManager.invalidate_api_prefix('stocks')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache stocks update: {e}")
        return instance

    def perform_destroy(self, instance):
        entrepot_id = instance.entrepot_id
        entreprise_id = instance.entrepot.entreprise_id if instance.entrepot else None
        instance.delete()
        try:
            if entrepot_id:
                CacheManager.invalidate_stocks_cache(entrepot_id)
            if entreprise_id:
                CacheManager.invalidate_produits_cache(entreprise_id)
            CacheManager.invalidate_api_prefix('stocks')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache stocks destroy: {e}")

# MouvementStock : historique des mouvements de stock
class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['produit', 'entrepot', 'type_mouvement', 'utilisateur', 'variante']
    search_fields = ['produit__nom', 'motif', 'reference_document']
    ordering_fields = ['created_at', 'quantite']
    
    def get_queryset(self):
        """Filtrer les mouvements par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()
        
        # Filtrer par entreprise de l'utilisateur connecté pour tous les rôles
        if self.request.user.entreprise:
            queryset = queryset.filter(entrepot__entreprise=self.request.user.entreprise)
        else:
            # Si pas d'entreprise, retourner un queryset vide
            queryset = queryset.none()
        
        return queryset.select_related('produit', 'entrepot', 'utilisateur', 'entrepot__entreprise')
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'transfert_stock'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminOrSuperAdmin]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        from .models import Stock, ProduitVariante
        from django.db import transaction

        produit_id = request.data.get('produit')
        entrepot_id = request.data.get('entrepot')
        variante_id = request.data.get('variante') or None
        type_mouvement = request.data.get('type_mouvement', 'entree')
        quantite = int(request.data.get('quantite', 0))

        if not produit_id or not entrepot_id or quantite < 1:
            return Response({'error': 'produit, entrepot et quantite sont requis'}, status=400)

        with transaction.atomic():
            # Récupérer ou créer le stock approprié
            stock_filter = dict(produit_id=produit_id, entrepot_id=entrepot_id)
            if variante_id:
                stock_filter['variante_id'] = variante_id
            else:
                stock_filter['variante__isnull'] = True

            stock = Stock.objects.select_for_update().filter(**stock_filter).first()
            if not stock:
                create_kwargs = dict(produit_id=produit_id, entrepot_id=entrepot_id, quantite=0)
                if variante_id:
                    create_kwargs['variante_id'] = variante_id
                stock = Stock.objects.create(**create_kwargs)

            quantite_avant = stock.quantite
            if type_mouvement == 'entree':
                quantite_apres = quantite_avant + quantite
            elif type_mouvement == 'sortie':
                quantite_apres = max(0, quantite_avant - quantite)
            elif type_mouvement == 'ajustement':
                quantite_apres = quantite
            else:
                quantite_apres = quantite_avant + quantite

            stock.quantite = quantite_apres
            stock.save(update_fields=['quantite', 'updated_at'])

            # Construire la data enrichie pour le serializer
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data['quantite_avant'] = quantite_avant
            data['quantite_apres'] = quantite_apres
            if variante_id:
                data['variante'] = variante_id

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Associer automatiquement l'utilisateur connecté au mouvement"""
        mouvement = serializer.save(utilisateur=self.request.user)
        # Invalidation des caches liés aux stocks et produits
        try:
            if mouvement.entrepot_id:
                CacheManager.invalidate_stocks_cache(mouvement.entrepot_id)
                if mouvement.entrepot and mouvement.entrepot.entreprise_id:
                    CacheManager.invalidate_produits_cache(mouvement.entrepot.entreprise_id)
            CacheManager.invalidate_api_prefix('stocks')
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur invalidation cache mouvements: {e}")
    
    @action(detail=False, methods=['post'], url_path='transfert')
    def transfert_stock(self, request):
        """Effectuer un transfert de stock entre entrepôts avec envoi d'emails"""
        try:
            from .utils import send_transfer_notification_emails
            from .models import Boutique, Stock, Produit
            
            # Récupérer les données du transfert
            produit_id = request.data.get('produit')
            entrepot_source_id = request.data.get('entrepot_source')
            entrepot_destination_id = request.data.get('entrepot_destination')
            quantite = request.data.get('quantite')
            motif = request.data.get('motif', '')
            
            # Validation des données
            if not all([produit_id, entrepot_source_id, entrepot_destination_id, quantite]):
                return Response({
                    'error': 'Tous les champs sont obligatoires'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier que les entrepôts appartiennent à la même entreprise
            entrepot_source = Boutique.objects.get(id=entrepot_source_id)
            entrepot_destination = Boutique.objects.get(id=entrepot_destination_id)
            
            if entrepot_source.entreprise != entrepot_destination.entreprise:
                return Response({
                    'error': 'Les entrepôts doivent appartenir à la même entreprise'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier le stock disponible
            try:
                stock_source = Stock.objects.get(
                    produit_id=produit_id,
                    entrepot_id=entrepot_source_id
                )
            except Stock.DoesNotExist:
                return Response({
                    'error': 'Stock non trouvé dans l\'entrepôt source'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if stock_source.quantite < quantite:
                return Response({
                    'error': f'Stock insuffisant. Disponible: {stock_source.quantite}, Demandé: {quantite}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer le produit
            produit = Produit.objects.get(id=produit_id)
            
            # Générer la référence du transfert
            reference_transfert = f"TRF-{entrepot_source.nom}-{entrepot_destination.nom}"
            
            # Créer le mouvement de sortie
            mouvement_sortie = MouvementStock.objects.create(
                produit=produit,
                entrepot=entrepot_source,
                type_mouvement='transfert',
                quantite=quantite,
                quantite_avant=stock_source.quantite,
                quantite_apres=stock_source.quantite - quantite,
                motif=f'Transfert vers {entrepot_destination.nom} - {motif}',
                reference_document=reference_transfert,
                utilisateur=request.user
            )
            
            # Mettre à jour le stock source
            stock_source.quantite -= quantite
            stock_source.save()
            
            # Créer ou mettre à jour le stock destination
            stock_destination, created = Stock.objects.get_or_create(
                produit=produit,
                entrepot=entrepot_destination,
                defaults={'quantite': quantite}
            )
            
            if not created:
                stock_destination.quantite += quantite
                stock_destination.save()
            
            # Créer le mouvement d'entrée
            mouvement_entree = MouvementStock.objects.create(
                produit=produit,
                entrepot=entrepot_destination,
                type_mouvement='transfert',
                quantite=quantite,
                quantite_avant=stock_destination.quantite - quantite if not created else 0,
                quantite_apres=stock_destination.quantite,
                motif=f'Transfert depuis {entrepot_source.nom} - {motif}',
                reference_document=reference_transfert,
                utilisateur=request.user
            )
            
            # Préparer les données pour l'envoi d'emails
            transfer_data = {
                'user_initiateur': request.user,
                'entreprise': entrepot_source.entreprise,
                'boutique_source': entrepot_source,
                'boutique_destination': entrepot_destination,
                'produit': produit.nom,
                'quantite': quantite,
                'motif': motif,
                'reference_transfert': reference_transfert
            }
            
            # Envoyer les emails de notification
            email_sent = send_transfer_notification_emails(transfer_data)
            
            return Response({
                'success': True,
                'message': 'Transfert effectué avec succès',
                'reference_transfert': reference_transfert,
                'mouvement_sortie_id': mouvement_sortie.id,
                'mouvement_entree_id': mouvement_entree.id,
                'emails_sent': email_sent
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Erreur lors du transfert: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Produit : gestion complète des produits
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entreprise', 'actif', 'categorie', 'fournisseur_principal', 'etat_produit']
    search_fields = ['nom', 'sku', 'reference', 'code_barres', 'description', 'marque', 'modele']
    ordering_fields = ['nom', 'prix_vente', 'quantite', 'created_at']
    # pagination_class = SmartPagination  # Désactivé pour maintenir la compatibilité
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filtrer les produits par entreprise de l'utilisateur connecté avec optimisations"""
        queryset = super().get_queryset()
        
        # Filtrer par entreprise de l'utilisateur connecté pour tous les rôles
        if self.request.user.entreprise:
            queryset = queryset.filter(entreprise=self.request.user.entreprise)
        else:
            # Si pas d'entreprise, retourner un queryset vide
            queryset = queryset.none()
        
        return queryset.select_related(
            'categorie',
            'entreprise',
            'fournisseur_principal'
        ).prefetch_related('stocks', 'variantes')
    
    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action in ('list', 'retrieve', 'stats'):
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAdminOrSuperAdmin, CanCreateProduit]
        elif self.action == 'import_produits':
            permission_classes = [IsAdminOrSuperAdmin, CanImportCSV]
        elif self.action == 'export_produits':
            permission_classes = [IsAdminOrSuperAdmin, CanExportCSV]
        else:
            permission_classes = [IsAdminOrSuperAdmin]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        try:
            # Forcer l'affectation à l'entreprise de l'utilisateur connecté
            entreprise = getattr(self.request.user, 'entreprise', None)
            if entreprise is None:
                raise serializers.ValidationError({'entreprise': 'Aucune entreprise associée à l’utilisateur.'})

            instance = serializer.save(entreprise=entreprise)
            create_journal_entry(
                user=self.request.user,
                type_operation='creation',
                description=f"Création du produit {instance.nom}",
                boutique=None,  # Plus de boutique dans le nouveau modèle
                details={
                    'produit_id': instance.id,
                    'nom': instance.nom,
                    'sku': instance.sku,
                    'prix_vente': float(instance.prix_vente),
                    'quantite': instance.quantite
                }
            )
            # Invalider le cache des produits de l'entreprise et les listes
            if instance.entreprise:
                CacheManager.invalidate_produits_cache(instance.entreprise.id)
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur lors de la création du produit: {str(e)}")
            raise

    def perform_update(self, serializer):
        try:
            # PROTECTION: empêcher la modification de l'entreprise
            current = self.get_object()
            if 'entreprise' in serializer.validated_data:
                serializer.validated_data['entreprise'] = current.entreprise

            instance = serializer.save()
            create_journal_entry(
                user=self.request.user,
                type_operation='modification',
                description=f"Modification du produit {instance.nom}",
                boutique=None,  # Plus de boutique dans le nouveau modèle
                details={
                    'produit_id': instance.id,
                    'nom': instance.nom,
                    'sku': instance.sku,
                    'prix_vente': float(instance.prix_vente),
                    'quantite': instance.quantite
                }
            )
            # Invalider le cache des produits de l'entreprise et les listes
            if instance.entreprise:
                CacheManager.invalidate_produits_cache(instance.entreprise.id)
            CacheManager.invalidate_api_prefix('produits')
        except Exception as e:
            print(f"Erreur lors de la mise à jour du produit: {str(e)}")
            raise

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrSuperAdmin, CanImportCSV])
    def import_produits(self, request):
        """Import de produits depuis un fichier CSV ou des données JSON"""
        try:
            # Vérifier si c'est un fichier CSV ou des données JSON
            if 'file' in request.FILES:
                # Import depuis fichier CSV
                file = request.FILES.get('file')
                if not file:
                    return Response({'error': 'Aucun fichier fourni'}, status=status.HTTP_400_BAD_REQUEST)
                
                if not file.name.endswith('.csv'):
                    return Response({'error': 'Seuls les fichiers CSV sont acceptés'}, status=status.HTTP_400_BAD_REQUEST)
                
                import csv
                import io
                
                # Lire le fichier CSV
                file_content = file.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(file_content))
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(csv_reader, start=2):  # Commencer à 2 car ligne 1 = headers
                    try:
                        # Préparer les données du produit
                        product_data = {
                            'nom': row.get('Nom', '').strip(),
                            'sku': row.get('SKU', '').strip() or None,
                            'description': row.get('Description', '').strip(),
                            'code_barres': row.get('Code-barres', '').strip() or None,
                            'prix_achat': float(row.get('Prix d\'achat', 0)) if row.get('Prix d\'achat') else 0,
                            'prix_vente': float(row.get('Prix de vente', 0)) if row.get('Prix de vente') else 0,
                            'prix_gros': float(row.get('Prix de gros', 0)) if row.get('Prix de gros') else None,
                            'stock_minimum': int(row.get('Stock minimum', 0)) if row.get('Stock minimum') else 0,
                            'stock_maximum': int(row.get('Stock maximum', 1000)) if row.get('Stock maximum') else 1000,
                            'unite_mesure': row.get('Unité de mesure', 'piece').strip(),
                            'etat_produit': row.get('État', 'neuf').strip(),
                            'marque': row.get('Marque', '').strip() or None,
                            'modele': row.get('Modèle', '').strip() or None,
                            'entreprise': request.user.entreprise.id if request.user.entreprise else None,
                            'actif': True
                        }
                        
                        # Validation des champs obligatoires
                        if not product_data['nom']:
                            errors.append(f"Ligne {row_num}: Nom du produit requis")
                            continue
                        
                        if product_data['prix_vente'] <= 0:
                            errors.append(f"Ligne {row_num}: Prix de vente doit être supérieur à 0")
                            continue
                        
                        # Créer le produit
                        serializer = self.get_serializer(data=product_data)
                        if serializer.is_valid():
                            serializer.save()
                            imported_count += 1
                        else:
                            errors.append(f"Ligne {row_num}: {serializer.errors}")
                            
                    except Exception as e:
                        errors.append(f"Ligne {row_num}: Erreur - {str(e)}")
                
                return Response({
                    'success': True,
                    'imported_count': imported_count,
                    'errors': errors[:10]  # Limiter à 10 erreurs
                })
                
            elif 'produits' in request.data:
                # Import depuis données JSON
                produits_data = request.data.get('produits', [])
                
                if not produits_data:
                    return Response({'error': 'Aucune donnée de produit fournie'}, status=status.HTTP_400_BAD_REQUEST)
                
                imported_count = 0
                errors = []
                
                for index, product_data in enumerate(produits_data):
                    try:
                        # Ajouter l'entreprise de l'utilisateur
                        product_data['entreprise'] = request.user.entreprise.id if request.user.entreprise else None
                        
                        # Validation des champs obligatoires
                        if not product_data.get('nom'):
                            errors.append(f"Produit {index + 1}: Nom du produit requis")
                            continue
                        
                        if not product_data.get('prix_vente') or product_data.get('prix_vente') <= 0:
                            errors.append(f"Produit {index + 1}: Prix de vente doit être supérieur à 0")
                            continue
                        
                        # Créer le produit
                        serializer = self.get_serializer(data=product_data)
                        if serializer.is_valid():
                            serializer.save()
                            imported_count += 1
                        else:
                            errors.append(f"Produit {index + 1}: {serializer.errors}")
                            
                    except Exception as e:
                        errors.append(f"Produit {index + 1}: Erreur - {str(e)}")
                
                return Response({
                    'success': True,
                    'imported_count': imported_count,
                    'errors': errors[:10]  # Limiter à 10 erreurs
                })
            
            else:
                return Response({'error': 'Aucun fichier ou données fournis'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error': f'Erreur lors de l\'import: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrSuperAdmin, CanExportCSV])
    def export_produits(self, request):
        """Export des produits vers un fichier CSV"""
        try:
            format_type = request.query_params.get('format', 'csv')
            entreprise_id = request.query_params.get('entreprise')
            
            if not entreprise_id:
                return Response({'error': 'ID entreprise requis'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Filtrer les produits par entreprise
            produits = self.get_queryset().filter(entreprise_id=entreprise_id)
            
            if format_type == 'csv':
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="produits_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
                
                # Ajouter BOM pour Excel
                response.write('\ufeff')
                
                writer = csv.writer(response)
                writer.writerow([
                    'Nom', 'SKU', 'Description', 'Code-barres', 'Référence',
                    'Prix d\'achat', 'Prix de vente', 'Prix de gros',
                    'Stock minimum', 'Stock maximum', 'Quantité actuelle',
                    'Catégorie', 'Fournisseur', 'Unité de mesure',
                    'Marque', 'Modèle', 'État', 'Créé le'
                ])
                
                for produit in produits:
                    writer.writerow([
                        produit.nom,
                        produit.sku or '',
                        produit.description or '',
                        produit.code_barres or '',
                        produit.reference or '',
                        produit.prix_achat,
                        produit.prix_vente,
                        produit.prix_gros or '',
                        produit.stock_minimum,
                        produit.stock_maximum,
                        produit.quantite,
                        produit.categorie.nom if produit.categorie else '',
                        produit.fournisseur_principal.nom if produit.fournisseur_principal else '',
                        produit.unite_mesure,
                        produit.marque or '',
                        produit.modele or '',
                        produit.etat_produit,
                        produit.created_at.strftime('%Y-%m-%d %H:%M') if produit.created_at else ''
                    ])
                
                return response
            
            else:
                return Response({'error': 'Format non supporté. Utilisez CSV.'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Agrégats stock calculés côté backend pour le dashboard."""
        from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
        qs = self.get_queryset()
        totals = qs.aggregate(
            total_produits=Count('id'),
            total_unites=Sum('quantite'),
            valeur_stock=Sum(
                ExpressionWrapper(F('quantite') * F('prix_vente'), output_field=FloatField())
            ),
            nb_rupture=Count('id', filter=django_models.Q(quantite=0)),
            nb_critique=Count('id', filter=django_models.Q(quantite__gt=0, quantite__lt=10)),
            nb_faible=Count('id', filter=django_models.Q(quantite__gte=10, quantite__lt=50)),
            nb_normal=Count('id', filter=django_models.Q(quantite__gte=50)),
        )
        return Response({
            'total_produits': totals['total_produits'] or 0,
            'total_unites': totals['total_unites'] or 0,
            'valeur_stock': round(totals['valeur_stock'] or 0, 2),
            'nb_rupture': totals['nb_rupture'] or 0,
            'nb_critique': totals['nb_critique'] or 0,
            'nb_faible': totals['nb_faible'] or 0,
            'nb_normal': totals['nb_normal'] or 0,
        })

# PrixProduit : visible uniquement par superadmin
class PrixProduitViewSet(viewsets.ModelViewSet):
    queryset = PrixProduit.objects.all()
    serializer_class = PrixProduitSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['produit']
    ordering_fields = ['date', 'prix_vente_yen']

# Partenaire : lié à la boutique, modifiable par admin ou superadmin
# Client : gestion des clients de l'entreprise
class SequenceFactureViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des séquences de numérotation des factures"""
    queryset = SequenceFacture.objects.all()
    serializer_class = SequenceFactureSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['boutique', 'annee', 'mois']
    ordering_fields = ['boutique', 'annee', 'mois', 'dernier_numero']
    ordering = ['boutique', 'annee', 'mois']
    
    def get_queryset(self):
        """Filtrer les séquences par entreprise (tous rôles)."""
        queryset = super().get_queryset()
        if self.request.user.entreprise:
            queryset = queryset.filter(boutique__entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        return queryset.select_related('boutique')
    
    @action(detail=False, methods=['get'])
    def get_next_number(self, request):
        """Obtenir le prochain numéro de facture pour une boutique"""
        boutique_id = request.query_params.get('boutique_id')
        if not boutique_id:
            return Response({'error': 'ID de boutique requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            boutique = Boutique.objects.get(id=boutique_id)
            numero = SequenceFacture.get_next_number(boutique)
            numero_complet = SequenceFacture.generate_invoice_number(boutique)
            
            return Response({
                'numero': numero,
                'numero_complet': numero_complet,
                'boutique': boutique.nom
            })
        except Boutique.DoesNotExist:
            return Response({'error': 'Boutique non trouvée'}, status=status.HTTP_404_NOT_FOUND)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['boutique', 'entreprise', 'actif']
    search_fields = ['nom', 'prenom', 'telephone', 'email']
    ordering_fields = ['nom', 'prenom', 'date_creation']
    ordering = ['nom', 'prenom']
    
    def get_queryset(self):
        """Filtrer les clients par entreprise de l'utilisateur connecté (tous rôles)."""
        queryset = super().get_queryset()
        if self.request.user.entreprise:
            queryset = queryset.filter(entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        return queryset.select_related('entreprise', 'boutique')
    
    def perform_create(self, serializer):
        """Créer un client avec l'entreprise de l'utilisateur connecté (tous rôles)."""
        if self.request.user.entreprise:
            serializer.save(entreprise=self.request.user.entreprise)
        else:
            serializer.save()
        try:
            CacheManager.invalidate_api_prefix('clients')
        except Exception as e:
            print(f"Erreur invalidation cache clients create: {e}")
    
    @action(detail=False, methods=['get'])
    def search_by_phone(self, request):
        """Rechercher un client par numéro de téléphone"""
        phone = request.query_params.get('phone', '')
        if not phone:
            return Response({'error': 'Numéro de téléphone requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        clients = self.get_queryset().filter(telephone__icontains=phone)
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)

class PartenaireViewSet(viewsets.ModelViewSet):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'boutique']
    search_fields = ['nom', 'prenom', 'telephone']
    ordering_fields = ['nom', 'dateadhesion']

    def get_queryset(self):
        """Filtrer les partenaires par boutique de l'utilisateur connecté."""
        queryset = super().get_queryset()
        user = self.request.user
        if user.boutique:
            queryset = queryset.filter(boutique=user.boutique)
        elif user.entreprise:
            # Filtre par toutes les boutiques de l'entreprise
            queryset = queryset.filter(boutique__entreprise=user.entreprise)
        else:
            queryset = queryset.none()
        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminOrSuperAdmin]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Forcer la boutique et l'entreprise lors de la création."""
        user = self.request.user
        kwargs = {}
        if user.boutique:
            kwargs['boutique'] = user.boutique
            kwargs['entreprise'] = user.boutique.entreprise
        elif user.entreprise:
            kwargs['entreprise'] = user.entreprise
        serializer.save(**kwargs)

# Facture : filtrable par type, boutique, status
class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FactureFilter
    search_fields = ['created_by__username']
    ordering_fields = ['total', 'reste', 'created_at']
    
    def get_queryset(self):
        """Filtrer les factures par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()
        user = self.request.user

        # Platform admin (superadmin sans entreprise) : peut filtrer par boutique/entreprise
        if user.role == 'superadmin' and not user.entreprise:
            boutique_id = self.request.query_params.get('boutique')
            entreprise_id = self.request.query_params.get('entreprise')
            if boutique_id:
                queryset = queryset.filter(boutique_id=boutique_id)
            elif entreprise_id:
                queryset = queryset.filter(boutique__entreprise_id=entreprise_id)
        elif user.entreprise:
            queryset = queryset.filter(boutique__entreprise=user.entreprise)
        else:
            queryset = queryset.none()

        return queryset.select_related('boutique', 'boutique__entreprise', 'created_by', 'client', 'partenaire')

    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action in ('list', 'retrieve'):
            permission_classes = [IsAuthenticated]
        elif self.action in ('create', 'create_with_stock'):
            permission_classes = [IsAuthenticated, CanCreateFacture]
        else:
            permission_classes = [IsAdminOrSuperAdmin]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('factures')
        except Exception as e:
            print(f"Erreur invalidation cache factures create: {e}")
        create_journal_entry(
            user=self.request.user,
            type_operation='creation',
            description=f"Création de la facture {instance.numero}",
            boutique=instance.boutique,
            details={
                'facture_id': instance.id,
                'numero': instance.numero,
                'type': instance.type,
                'total': instance.total,
                'reste': instance.reste
            }
        )

    @action(detail=False, methods=['post'], url_path='create-with-stock')
    def create_with_stock(self, request):
        """Créer une facture + commandes + mise à jour stock en transaction"""
        transaction_serializer = FactureTransactionSerializer(data=request.data)
        transaction_serializer.is_valid(raise_exception=True)

        data = transaction_serializer.validated_data
        boutique = data['boutique']

        # Sécurité: boutique doit appartenir à l'entreprise de l'utilisateur
        if request.user.entreprise and boutique.entreprise_id != request.user.entreprise_id:
            return Response(
                {'error': "Boutique non autorisée"},
                status=status.HTTP_403_FORBIDDEN
            )

        items = data['items']
        produit_ids = [item['produit'].id for item in items]
        variante_ids = [item['variante'].id for item in items if item.get('variante')]

        with transaction.atomic():
            # Verrouiller les stocks concernés — produit-niveau ET variante-niveau
            stocks_qs = Stock.objects.select_for_update().filter(
                entrepot=boutique,
                produit_id__in=produit_ids
            )
            # Clé : (produit_id, variante_id) — None pour produit sans variante
            stocks_map = {}
            for s in stocks_qs:
                key = (s.produit_id, s.variante_id)
                stocks_map[key] = s

            def get_stock(item):
                v = item.get('variante')
                key = (item['produit'].id, v.id if v else None)
                return stocks_map.get(key)

            # Vérifier stock suffisant
            for item in items:
                stock = get_stock(item)
                v = item.get('variante')
                label = f"{item['produit'].nom}{(' — ' + v.nom) if v else ''}"
                if not stock:
                    raise serializers.ValidationError(
                        f"Stock introuvable pour {label}"
                    )
                if stock.quantite < item['quantite']:
                    raise serializers.ValidationError(
                        f"Stock insuffisant pour {label} (disponible: {stock.quantite})"
                    )

            # Créer la facture
            facture = Facture.objects.create(
                type=data['type'],
                total=data['total'],
                reste=data['reste'],
                status=data.get('status', 'En attente'),
                client=data.get('client'),
                partenaire=data.get('partenaire'),
                boutique=boutique,
                created_by=request.user,
                entreprise=boutique.entreprise
            )

            # Enregistrer le versement initial saisi à la facturation
            montant_verse_initial = float(data['total']) - float(data['reste'])
            if montant_verse_initial > 0:
                Versement.objects.create(
                    facture=facture,
                    montant=montant_verse_initial,
                    created_by=request.user,
                    boutique=boutique,
                )

            commandes = []
            mouvements = []

            # Créer commandes + mouvements + mise à jour stock
            for item in items:
                variante = item.get('variante')
                stock = get_stock(item)
                quantite_avant = stock.quantite
                quantite_apres = quantite_avant - item['quantite']

                commande_kwargs = dict(
                    facture=facture,
                    produit=item['produit'],
                    variante=variante,
                    quantite=item['quantite'],
                    prix_unitaire_fcfa=item['prix_unitaire_fcfa'],
                    prix_initial_fcfa=item.get('prix_initial_fcfa') or item['prix_unitaire_fcfa'],
                    justification_prix=item.get('justification_prix') or ''
                )
                if data['type'] == 'client':
                    commande = CommandeClient.objects.create(**commande_kwargs)
                else:
                    commande = CommandePartenaire.objects.create(**commande_kwargs)

                commandes.append(commande)

                # Mettre à jour le stock
                stock.quantite = quantite_apres
                stock.save(update_fields=['quantite', 'updated_at'])

                # Créer mouvement stock
                mouvement = MouvementStock.objects.create(
                    produit=item['produit'],
                    variante=variante,
                    entrepot=boutique,
                    type_mouvement='sortie',
                    quantite=item['quantite'],
                    quantite_avant=quantite_avant,
                    quantite_apres=quantite_apres,
                    motif=f"Vente - Facture {facture.numero}",
                    reference_document=facture.numero,
                    utilisateur=request.user,
                )
                mouvements.append(mouvement)

                # Journal par ligne
                try:
                    create_journal_entry(
                        user=request.user,
                        type_operation='vente',
                        description=f"Vente de {commande.quantite} {commande.produit.nom}",
                        boutique=facture.boutique,
                        details={
                            'commande_id': commande.id,
                            'produit': commande.produit.nom,
                            'quantite': commande.quantite,
                            'prix_unitaire': commande.prix_unitaire_fcfa,
                            'total': commande.total
                        }
                    )
                except Exception:
                    pass

            # Journal facture
            try:
                create_journal_entry(
                    user=request.user,
                    type_operation='creation',
                    description=f"Création de la facture {facture.numero}",
                    boutique=facture.boutique,
                    details={
                        'facture_id': facture.id,
                        'numero': facture.numero,
                        'type': facture.type,
                        'total': facture.total,
                        'reste': facture.reste
                    }
                )
            except Exception:
                pass

            # Invalidation cache
            try:
                CacheManager.invalidate_api_prefix('factures')
                CacheManager.invalidate_api_prefix('commandes-client')
                CacheManager.invalidate_api_prefix('commandes-partenaire')
                CacheManager.invalidate_api_prefix('stocks')
                CacheManager.invalidate_api_prefix('mouvements-stock')
            except Exception:
                pass

            # Réponse
            facture_data = FactureSerializer(facture).data
            if data['type'] == 'client':
                commandes_data = CommandeClientSerializer(commandes, many=True).data
            else:
                commandes_data = CommandePartenaireSerializer(commandes, many=True).data

            return Response(
                {
                    'success': True,
                    'facture': facture_data,
                    'commandes': commandes_data
                },
                status=status.HTTP_201_CREATED
            )

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            CacheManager.invalidate_api_prefix('factures')
        except Exception as e:
            print(f"Erreur invalidation cache factures update: {e}")
        create_journal_entry(
            user=self.request.user,
            type_operation='modification',
            description=f"Modification de la facture {instance.numero}",
            boutique=instance.boutique,
            details={
                'facture_id': instance.id,
                'numero': instance.numero,
                'type': instance.type,
                'total': instance.total,
                'reste': instance.reste,
                'status': instance.status
            }
        )

    @action(detail=True, methods=['post'], url_path='annuler', permission_classes=[IsAdminOrSuperAdmin])
    def annuler_facture(self, request, pk=None):
        """Annuler une facture et remettre le stock"""
        facture = self.get_object()

        if facture.status == 'Annulée':
            return Response({'error': 'Cette facture est déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Récupérer toutes les commandes
            if facture.type == 'client':
                commandes = list(facture.commandes_client.select_related('produit').all())
            else:
                commandes = list(facture.commandes_partenaire.select_related('produit').all())

            for commande in commandes:
                # Retrouver ou créer le stock
                stock = Stock.objects.select_for_update().filter(
                    entrepot=facture.boutique,
                    produit=commande.produit
                ).first()

                if stock:
                    quantite_avant = stock.quantite
                    stock.quantite += commande.quantite
                    stock.save()

                    MouvementStock.objects.create(
                        produit=commande.produit,
                        entrepot=facture.boutique,
                        type_mouvement='entree',
                        quantite=commande.quantite,
                        quantite_avant=quantite_avant,
                        quantite_apres=stock.quantite,
                        motif=f"Annulation facture {facture.numero}",
                        reference_document=facture.numero,
                        utilisateur=request.user,
                    )

            # Annuler la facture
            facture.status = 'Annulée'
            facture.save()

            # Journal
            try:
                create_journal_entry(
                    user=request.user,
                    type_operation='modification',
                    description=f"Annulation de la facture {facture.numero}",
                    boutique=facture.boutique,
                    details={
                        'facture_id': facture.id,
                        'numero': facture.numero,
                        'type': facture.type,
                        'total': facture.total,
                        'nb_produits': len(commandes)
                    }
                )
            except Exception:
                pass

            # Invalidation cache
            try:
                CacheManager.invalidate_api_prefix('factures')
                CacheManager.invalidate_api_prefix('stocks')
                CacheManager.invalidate_api_prefix('mouvements-stock')
            except Exception:
                pass

        return Response({'success': True, 'message': f'Facture {facture.numero} annulée avec succès.'})

    @action(detail=False, methods=['get'], url_path='analytics', permission_classes=[IsAuthenticated])
    def analytics(self, request):
        """
        Statistiques CA par période (jour/semaine/mois).
        Params: date_debut, date_fin, boutique, granularite (jour|semaine|mois)
        """
        from django.db.models import Sum, Count, Q, F
        from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
        from datetime import datetime, timedelta
        import json

        boutique_id = request.query_params.get('boutique')
        date_debut_str = request.query_params.get('date_debut')
        date_fin_str = request.query_params.get('date_fin')
        granularite = request.query_params.get('granularite', 'jour')

        qs = self.get_queryset().exclude(status='Annulée')

        if boutique_id:
            qs = qs.filter(boutique_id=boutique_id)

        # Période par défaut : 30 derniers jours
        now = timezone.now()
        if date_debut_str:
            try:
                date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            except ValueError:
                date_debut = (now - timedelta(days=30)).date()
        else:
            date_debut = (now - timedelta(days=30)).date()

        if date_fin_str:
            try:
                date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
            except ValueError:
                date_fin = now.date()
        else:
            date_fin = now.date()

        qs = qs.filter(created_at__date__gte=date_debut, created_at__date__lte=date_fin)

        # Choisir la granularité
        trunc_fn = {'semaine': TruncWeek, 'mois': TruncMonth}.get(granularite, TruncDay)

        serie = (
            qs.annotate(periode=trunc_fn('created_at'))
            .values('periode')
            .annotate(
                ca=Sum('total'),
                nb_factures=Count('id'),
                montant_verse=Sum('total') - Sum('reste'),
            )
            .order_by('periode')
        )

        # KPIs globaux de la période
        totaux = qs.aggregate(
            ca_total=Sum('total'),
            total_verse=Sum('total') - Sum('reste'),
            total_reste=Sum('reste'),
            nb_factures=Count('id'),
            nb_payees=Count('id', filter=Q(status='Payé')),
            nb_partielles=Count('id', filter=Q(status='Partiellement payé')),
            nb_attente=Count('id', filter=Q(status='En attente')),
        )

        ca_clients = qs.filter(type='client').aggregate(ca=Sum('total'))['ca'] or 0
        ca_partenaires = qs.filter(type='partenaire').aggregate(ca=Sum('total'))['ca'] or 0

        # Top 5 produits (par CA) via commandes_client + commandes_partenaire
        from .models import CommandeClient, CommandePartenaire
        facture_ids = list(qs.values_list('id', flat=True))

        top_produits_client = (
            CommandeClient.objects.filter(facture_id__in=facture_ids)
            .values('produit__nom')
            .annotate(ca=Sum(F('quantite') * F('prix_unitaire_fcfa')), qte=Sum('quantite'))
            .order_by('-ca')[:5]
        )
        top_produits_partenaire = (
            CommandePartenaire.objects.filter(facture_id__in=facture_ids)
            .values('produit__nom')
            .annotate(ca=Sum(F('quantite') * F('prix_unitaire_fcfa')), qte=Sum('quantite'))
            .order_by('-ca')[:5]
        )

        # Fusionner + trier top produits
        produits_dict = {}
        for p in list(top_produits_client) + list(top_produits_partenaire):
            nom = p['produit__nom']
            if nom not in produits_dict:
                produits_dict[nom] = {'nom': nom, 'ca': 0, 'qte': 0}
            produits_dict[nom]['ca'] += p['ca'] or 0
            produits_dict[nom]['qte'] += p['qte'] or 0
        top_produits = sorted(produits_dict.values(), key=lambda x: x['ca'], reverse=True)[:5]

        # Top 5 clients
        top_clients = (
            qs.filter(type='client', client__isnull=False)
            .values('client__nom', 'client__prenom')
            .annotate(ca=Sum('total'), nb=Count('id'))
            .order_by('-ca')[:5]
        )

        # Top 5 partenaires
        top_partenaires = (
            qs.filter(type='partenaire', partenaire__isnull=False)
            .values('partenaire__nom', 'partenaire__prenom')
            .annotate(ca=Sum('total'), nb=Count('id'))
            .order_by('-ca')[:5]
        )

        return Response({
            'periode': {'debut': str(date_debut), 'fin': str(date_fin), 'granularite': granularite},
            'kpis': {
                'ca_total': round(totaux['ca_total'] or 0, 2),
                'total_verse': round(totaux['total_verse'] or 0, 2),
                'total_reste': round(totaux['total_reste'] or 0, 2),
                'nb_factures': totaux['nb_factures'] or 0,
                'nb_payees': totaux['nb_payees'] or 0,
                'nb_partielles': totaux['nb_partielles'] or 0,
                'nb_attente': totaux['nb_attente'] or 0,
                'ca_clients': round(ca_clients, 2),
                'ca_partenaires': round(ca_partenaires, 2),
            },
            'serie': [
                {
                    'date': s['periode'].strftime('%Y-%m-%d') if s['periode'] else None,
                    'ca': round(s['ca'] or 0, 2),
                    'nb_factures': s['nb_factures'] or 0,
                    'montant_verse': round(s['montant_verse'] or 0, 2),
                }
                for s in serie
            ],
            'top_produits': list(top_produits),
            'top_clients': [
                {'nom': f"{c['client__prenom']} {c['client__nom']}".strip(), 'ca': round(c['ca'] or 0, 2), 'nb': c['nb']}
                for c in top_clients
            ],
            'top_partenaires': [
                {'nom': f"{p['partenaire__prenom']} {p['partenaire__nom']}".strip(), 'ca': round(p['ca'] or 0, 2), 'nb': p['nb']}
                for p in top_partenaires
            ],
        })

# Commande Client
class CommandeClientViewSet(viewsets.ModelViewSet):
    queryset = CommandeClient.objects.select_related('produit', 'variante', 'facture').all()
    serializer_class = CommandeClientSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture', 'produit']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'superadmin' and not user.entreprise:
            return qs
        if user.entreprise:
            return qs.filter(facture__boutique__entreprise=user.entreprise)
        return qs.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        return [IsAdminOrSuperAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='vente',
            description=f"Vente de {instance.quantite} {instance.produit.nom}",
            boutique=instance.facture.boutique,
            details={
                'commande_id': instance.id,
                'produit': instance.produit.nom,
                'quantite': instance.quantite,
                'prix_unitaire': instance.prix_unitaire_fcfa,
                'total': instance.total
            }
        )

# Commande Partenaire
class CommandePartenaireViewSet(viewsets.ModelViewSet):
    queryset = CommandePartenaire.objects.select_related('produit', 'variante', 'facture').all()
    serializer_class = CommandePartenaireSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    
    def get_permissions(self):
        """
        Permettre la lecture (GET) pour tous les utilisateurs authentifiés,
        mais restreindre les modifications aux admins/superadmins.
        """
        if self.action in ['list', 'retrieve']:
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        return [IsAdminOrSuperAdmin()]
    filterset_fields = ['facture', 'produit']  # 'partenaire' n'existe pas directement sur CommandePartenaire, il est via facture.partenaire
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == 'superadmin' and not user.entreprise:
            return queryset.select_related('produit', 'facture', 'facture__boutique', 'facture__partenaire')
        if user.entreprise:
            return queryset.filter(facture__boutique__entreprise=user.entreprise).select_related('produit', 'facture', 'facture__boutique', 'facture__partenaire')
        return queryset.none()

    def perform_create(self, serializer):
        instance = serializer.save()
        create_journal_entry(
            user=self.request.user,
            type_operation='achat',
            description=f"Achat de {instance.quantite} {instance.produit.nom}",
            boutique=instance.facture.boutique,
            details={
                'commande_id': instance.id,
                'produit': instance.produit.nom,
                'quantite': instance.quantite,
                'prix_unitaire': instance.prix_unitaire_fcfa,
                'total': instance.total
            }
        )

# Versement : tous les versements d'une facture
class VersementViewSet(viewsets.ModelViewSet):
    queryset = Versement.objects.all()
    serializer_class = VersementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facture']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminOrSuperAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'superadmin' and not user.entreprise:
            return qs
        if user.entreprise:
            return qs.filter(facture__boutique__entreprise=user.entreprise)
        return qs.none()

    def perform_create(self, serializer):
        from django.db.models import Sum
        boutique = self.request.user.boutique if hasattr(self.request.user, 'boutique') else None
        if not boutique:
            boutique = serializer.validated_data['facture'].boutique

        instance = serializer.save(created_by=self.request.user, boutique=boutique)

        # Recalculer reste et statut automatiquement à partir de tous les versements
        facture = instance.facture
        total_verse = facture.versements.aggregate(total=Sum('montant'))['total'] or 0
        facture.reste = max(0.0, float(facture.total) - float(total_verse))
        if facture.reste <= 0:
            facture.status = 'Payé'
        elif total_verse > 0:
            facture.status = 'Partiellement payé'
        facture.save(update_fields=['reste', 'status'])

        create_journal_entry(
            user=self.request.user,
            type_operation='modification',
            description=f"Versement de {instance.montant} XAF pour la facture {instance.facture.numero}",
            boutique=instance.facture.boutique,
            details={
                'versement_id': instance.id,
                'facture': instance.facture.numero,
                'montant': float(instance.montant),
                'reste': facture.reste,
                'date': str(instance.date_versement)
            }
        )

# Historique des stocks : utile pour audit
class HistoriqueStockViewSet(viewsets.ModelViewSet):
    queryset = HistoriqueStock.objects.all()
    serializer_class = HistoriqueStockSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['produit', 'user']
    search_fields = ['motif']

class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['date_operation', 'type_operation', 'utilisateur']
    ordering = ['-date_operation']

    def get_queryset(self):
        user = self.request.user
        # Isolation par entreprise
        if user.role == 'superadmin' and not user.entreprise:
            queryset = Journal.objects.all()
        elif user.entreprise:
            queryset = Journal.objects.filter(boutique__entreprise=user.entreprise)
        else:
            return Journal.objects.none()

        boutique = self.request.query_params.get('boutique')
        type_operation = self.request.query_params.get('type_operation')
        utilisateur = self.request.query_params.get('utilisateur')
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')

        if boutique:
            queryset = queryset.filter(boutique_id=boutique)
        if type_operation:
            queryset = queryset.filter(type_operation=type_operation)
        if utilisateur:
            queryset = queryset.filter(utilisateur_id=utilisateur)
        if date_debut:
            queryset = queryset.filter(date_operation__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_operation__lte=date_fin)

        return queryset.select_related('utilisateur', 'boutique')

    def perform_create(self, serializer):
        try:
            serializer.save(utilisateur=self.request.user)
        except Exception as e:
            print(f"Erreur lors de la création du journal: {str(e)}")
            raise

# Fonction utilitaire pour créer des entrées de journal
def create_journal_entry(user, type_operation, description, boutique=None, details=None):
    try:
        from .utils import get_user_display_name
        user_label = get_user_display_name(user)
        if user_label and user_label not in description:
            description = f"{user_label} — {description}"
        journal_details = dict(details or {})
        journal_details.setdefault('utilisateur', user_label)
        if user and getattr(user, 'id', None):
            journal_details.setdefault('utilisateur_id', user.id)
        entreprise = None
        if boutique and getattr(boutique, 'entreprise', None):
            entreprise = boutique.entreprise
        elif user and getattr(user, 'entreprise', None):
            entreprise = user.entreprise
        Journal.objects.create(
            utilisateur=user,
            entreprise=entreprise,
            boutique=boutique,
            type_operation=type_operation,
            description=description,
            details=journal_details,
            ip_address=None,
        )
    except Exception as e:
        print(f"Erreur lors de la création du journal: {str(e)}")

# Vue pour le formulaire de contact

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Enregistre la déconnexion dans le journal."""
    try:
        user = request.user
        boutique = getattr(user, 'boutique', None)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        Journal.objects.create(
            utilisateur=user,
            entreprise=getattr(boutique, 'entreprise', None) if boutique else None,
            boutique=boutique,
            type_operation='deconnexion',
            description=f"{user.get_full_name() or user.username} s'est déconnecté(e)",
            ip_address=ip or None,
        )
    except Exception:
        pass
    return Response({'detail': 'Déconnexion enregistrée.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_form_submit(request):
    """
    API pour soumettre le formulaire de contact depuis le site web
    """
    try:
        # Récupérer les données du formulaire
        data = request.data
        
        # Validation des champs requis
        required_fields = ['fullname', 'email', 'phone', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'success': False,
                    'error': f'Le champ {field} est requis'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Préparer les données pour l'email
        email_data = {
            'fullname': data['fullname'],
            'email': data['email'],
            'phone': data['phone'],
            'company': data.get('company', 'Non spécifiée'),
            'subject': data['subject'],
            'message': data['message'],
            'timestamp': timezone.now().strftime('%d/%m/%Y à %H:%M')
        }
        
        # Rendre le template HTML
        html_content = render_to_string('emails/contact_form_email.html', email_data)
        
        # Créer le contenu texte simple
        text_content = f"""
Nouvelle demande de contact - Mura Storage

Informations du client:
- Nom: {email_data['fullname']}
- Email: {email_data['email']}
- Téléphone: {email_data['phone']}
- Entreprise: {email_data['company']}
- Sujet: {email_data['subject']}
- Date: {email_data['timestamp']}

Message:
{email_data['message']}

Ce client souhaite obtenir plus d'informations sur Mura Storage.
        """
        
        # Envoyer l'email
        send_mail(
            subject=f"Nouvelle demande de contact - {email_data['subject']}",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['wilfriedtayou6@gmail.com'],
            html_message=html_content,
            fail_silently=False,
        )
        
        # Log pour le suivi
        print(f"📧 Email de contact envoyé:")
        print(f"   Client: {email_data['fullname']} ({email_data['email']})")
        print(f"   Sujet: {email_data['subject']}")
        print(f"   Timestamp: {email_data['timestamp']}")
        
        return Response({
            'success': True,
            'message': 'Votre message a été envoyé avec succès ! Nous vous contacterons bientôt.',
            'timestamp': email_data['timestamp']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de contact: {str(e)}")
        return Response({
            'success': False,
            'error': 'Une erreur est survenue lors de l\'envoi de votre message. Veuillez réessayer.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============== GESTION DE LA RÉINITIALISATION DE MOT DE PASSE ==============

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Demande de réinitialisation de mot de passe
    POST /api/password-reset/request/
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Chercher l'utilisateur
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on ne révèle pas si l'email existe ou non
            return Response({
                'success': True,
                'message': 'Si cet email existe dans notre système, vous recevrez un lien de réinitialisation.'
            }, status=status.HTTP_200_OK)
        
        # Générer le token
        token = PasswordResetManager.generate_reset_token(user)
        
        # Envoyer l'email
        email_sent = PasswordResetManager.send_reset_email(user, token)
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Un email de réinitialisation a été envoyé à votre adresse.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirmation de réinitialisation de mot de passe
    POST /api/password-reset/confirm/
    """
    try:
        email = request.data.get('email')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not email or not token or not new_password:
            return Response({
                'success': False,
                'error': 'Email, token et nouveau mot de passe sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier la validité du token
        user = PasswordResetManager.verify_reset_token(token, email)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Token invalide ou expiré'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier la longueur du mot de passe
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'Le mot de passe doit contenir au moins 8 caractères'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Une erreur est survenue lors de la réinitialisation.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== VIEWSETS D'INVENTAIRE ====================

class InventaireViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les inventaires"""
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'entrepot', 'entreprise', 'responsable']
    search_fields = ['nom', 'numero', 'description']
    ordering_fields = ['created_at', 'date_debut', 'statut']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrer les inventaires par entreprise de l'utilisateur connecté"""
        queryset = super().get_queryset()
        
        # Filtrer par entreprise de l'utilisateur connecté
        if self.request.user.entreprise:
            queryset = queryset.filter(entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        
        # Optimisations
        return queryset.select_related(
            'entrepot', 'entreprise', 'responsable', 'created_by'
        ).prefetch_related('produits__produit')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InventaireCreateSerializer
        return InventaireSerializer
    
    def create(self, request, *args, **kwargs):
        """Créer un inventaire et initialiser les produits"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Ajouter l'entreprise de l'utilisateur connecté
        entreprise = request.user.entreprise
        if not entreprise:
            return Response({
                'error': 'Vous devez être associé à une entreprise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.validated_data['entreprise'] = entreprise
        serializer.validated_data['created_by'] = request.user
        
        # Créer l'inventaire
        inventaire = serializer.save()
        
        # Initialiser tous les produits de l'entrepôt
        entrepot = inventaire.entrepot
        
        # Récupérer tous les stocks de cet entrepôt
        stocks = Stock.objects.filter(entrepot=entrepot, produit__entreprise=entreprise)
        
        # Créer les entrées d'inventaire pour chaque produit
        for stock in stocks:
            InventaireProduit.objects.create(
                inventaire=inventaire,
                produit=stock.produit,
                quantite_theorique=stock.quantite
            )
        
        # Mettre à jour le nombre total de produits
        inventaire.total_produits = stocks.count()
        inventaire.save()
        
        return Response(self.serializer_class(inventaire).data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Récupérer les détails d'un inventaire avec tous ses produits"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class InventaireProduitViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les produits d'un inventaire"""
    queryset = InventaireProduit.objects.all()
    serializer_class = InventaireProduitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['inventaire', 'est_compte']
    search_fields = ['produit__nom', 'produit__sku', 'produit__reference']
    
    def get_queryset(self):
        """Filtrer par entreprise de l'utilisateur"""
        queryset = super().get_queryset()
        
        if self.request.user.entreprise:
            queryset = queryset.filter(inventaire__entreprise=self.request.user.entreprise)
        else:
            queryset = queryset.none()
        
        return queryset.select_related('produit', 'inventaire', 'compteur')
    
    def update(self, request, *args, **kwargs):
        """Mettre à jour un produit d'inventaire (comptage)"""
        instance = self.get_object()
        
        # Vérifier que l'inventaire est en cours
        if instance.inventaire.statut != 'en_cours':
            return Response({
                'error': f'Cet inventaire est {instance.inventaire.get_statut_display()}. Le comptage n\'est pas possible.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quantite_reelle = request.data.get('quantite_reelle')
        commentaire = request.data.get('commentaire', '')
        
        if quantite_reelle is None:
            return Response({
                'error': 'La quantité réelle est requise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marquer comme compté
        instance.marquer_compte(quantite_reelle, request.user, commentaire)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demarrer_inventaire(request, pk):
    """Action pour démarrer un inventaire"""
    try:
        inventaire = Inventaire.objects.get(pk=pk)
        
        # Vérifier que l'utilisateur peut démarrer cet inventaire
        if inventaire.entreprise != request.user.entreprise:
            return Response({
                'error': 'Vous n\'avez pas les permissions pour démarrer cet inventaire'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if inventaire.statut != 'planifie':
            return Response({
                'error': f'Cet inventaire est déjà {inventaire.get_statut_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        inventaire.mark_as_started()
        
        return Response({
            'success': True,
            'message': 'Inventaire démarré avec succès',
            'inventaire': InventaireSerializer(inventaire).data
        })
    except Inventaire.DoesNotExist:
        return Response({
            'error': 'Inventaire non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminer_inventaire(request, pk):
    """Action pour terminer un inventaire"""
    try:
        inventaire = Inventaire.objects.get(pk=pk)
        
        # Vérifier les permissions
        if inventaire.entreprise != request.user.entreprise:
            return Response({
                'error': 'Vous n\'avez pas les permissions pour terminer cet inventaire'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if inventaire.statut != 'en_cours':
            return Response({
                'error': f'Cet inventaire est {inventaire.get_statut_display()}. Impossible de terminer.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que les stocks ont été ajustés avant de terminer
        if not inventaire.stocks_ajustes:
            return Response({
                'error': 'Vous devez d\'abord ajuster les stocks avant de terminer l\'inventaire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Terminer l'inventaire
        inventaire.mark_as_completed()
        
        return Response({
            'success': True,
            'message': 'Inventaire terminé avec succès',
            'inventaire': InventaireSerializer(inventaire).data
        })
    except Inventaire.DoesNotExist:
        return Response({
            'error': 'Inventaire non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ajuster_stocks_inventaire(request, pk):
    """Ajuster les stocks suite à un inventaire"""
    try:
        inventaire = Inventaire.objects.get(pk=pk)
        
        # Vérifier les permissions
        if inventaire.entreprise != request.user.entreprise:
            return Response({
                'error': 'Vous n\'avez pas les permissions pour ajuster les stocks de cet inventaire'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier le statut
        if inventaire.statut != 'en_cours':
            return Response({
                'error': 'Cet inventaire doit être en cours pour ajuster les stocks'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si déjà ajusté
        if inventaire.stocks_ajustes:
            return Response({
                'error': 'Les stocks ont déjà été ajustés pour cet inventaire'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Ajuster les stocks
        resultat = inventaire.ajuster_stocks(request.user)
        
        if 'error' in resultat:
            return Response({
                'error': resultat['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Recharger l'inventaire pour avoir les données à jour
        inventaire.refresh_from_db()
        
        # Invalider le cache des stocks
        if inventaire.entrepot:
            CacheManager.invalidate_stocks_cache(inventaire.entrepot.id)
        if inventaire.entreprise:
            CacheManager.invalidate_produits_cache(inventaire.entreprise.id)
        
        return Response({
            'success': True,
            'message': resultat['message'],
            'ajustements_faits': resultat['ajustements_faits'],
            'mouvements_crees': resultat['mouvements_crees'],
            'inventaire': InventaireSerializer(inventaire).data
        })
        
    except Inventaire.DoesNotExist:
        return Response({
            'error': 'Inventaire non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERREUR lors de l'ajustement des stocks (Inventaire {pk}):")
        print(f"Erreur: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        return Response({
            'error': f'Erreur lors de l\'ajustement des stocks: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ExerciceFiscalViewSet(viewsets.ModelViewSet):
    """CRUD + actions cloture/ouverture pour les exercices fiscaux."""
    serializer_class = ExerciceFiscalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ExerciceFiscal.objects.select_related('entreprise', 'cloture_par')
        entreprise_id = self.request.query_params.get('entreprise')
        if entreprise_id:
            qs = qs.filter(entreprise_id=entreprise_id)
        else:
            user = self.request.user
            if hasattr(user, 'entreprise') and user.entreprise:
                qs = qs.filter(entreprise=user.entreprise)
            elif hasattr(user, 'boutique') and user.boutique and user.boutique.entreprise:
                qs = qs.filter(entreprise=user.boutique.entreprise)
        return qs

    @action(detail=False, methods=['get'], url_path='courant')
    def exercice_courant(self, request):
        """Retourne l''exercice ouvert de l''annee courante, le cree si absent."""
        from django.utils import timezone
        entreprise_id = request.query_params.get('entreprise')
        if not entreprise_id:
            user = request.user
            if hasattr(user, 'entreprise') and user.entreprise:
                entreprise_id = user.entreprise.id
            elif hasattr(user, 'boutique') and user.boutique and user.boutique.entreprise:
                entreprise_id = user.boutique.entreprise.id
            else:
                return Response({'error': 'entreprise requis'}, status=400)
        annee = int(request.query_params.get('annee', timezone.now().year))
        try:
            exercice, created = ExerciceFiscal.get_or_create_for_entreprise(int(entreprise_id), annee)
            return Response(ExerciceFiscalSerializer(exercice).data, status=201 if created else 200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'], url_path='cloture')
    def cloture(self, request, pk=None):
        """Cloturer un exercice : snapshot + verrouillage."""
        from django.utils import timezone
        exercice = self.get_object()
        if exercice.statut == 'cloture':
            return Response({'error': 'Cet exercice est deja cloture.'}, status=400)
        boutiques = Boutique.objects.filter(entreprise=exercice.entreprise)
        date_debut = exercice.date_debut
        date_fin = exercice.date_fin
        factures_qs = Facture.objects.filter(
            boutique__in=boutiques,
            created_at__date__gte=date_debut,
            created_at__date__lte=date_fin,
            status__in=['Payé', 'Partiellement payé', 'En attente'],
        )
        ca = factures_qs.aggregate(total=Sum('total'))['total'] or 0
        nb_factures = factures_qs.count()
        stocks = Stock.objects.filter(entrepot__in=boutiques).select_related('produit')
        valeur_stock = sum(
            (s.quantite or 0) * float(s.produit.prix_vente or s.produit.prix or 0)
            for s in stocks
        )
        nb_produits = Produit.objects.filter(entreprise=exercice.entreprise, actif=True).count()
        from django.db.models import F
        total_achats = MouvementStock.objects.filter(
            entrepot__in=boutiques,
            type_mouvement='entree',
            created_at__date__gte=date_debut,
            created_at__date__lte=date_fin,
        ).aggregate(total=Sum(F('quantite') * F('produit__prix_achat')))['total'] or 0
        exercice.chiffre_affaires = ca
        exercice.total_achats = total_achats
        exercice.nb_factures = nb_factures
        exercice.valeur_stock_cloture = valeur_stock
        exercice.nb_produits = nb_produits
        exercice.benefice_net = float(ca) - float(total_achats)
        exercice.statut = 'cloture'
        exercice.cloture_par = request.user
        exercice.date_cloture = timezone.now()
        exercice.notes = request.data.get('notes', '')
        exercice.save()
        return Response(ExerciceFiscalSerializer(exercice).data)

    @action(detail=False, methods=['post'], url_path='ouvrir')
    def ouvrir_nouvel_exercice(self, request):
        """Ouvrir un nouvel exercice pour l''annee indiquee."""
        from django.utils import timezone
        entreprise_id = request.data.get('entreprise')
        annee = int(request.data.get('annee', timezone.now().year))
        if not entreprise_id:
            return Response({'error': 'entreprise requis'}, status=400)
        try:
            exercice, created = ExerciceFiscal.get_or_create_for_entreprise(int(entreprise_id), annee)
            if not created:
                return Response({'message': f'Exercice {annee} existe deja.', 'exercice': ExerciceFiscalSerializer(exercice).data})
            return Response(ExerciceFiscalSerializer(exercice).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'], url_path='rapport')
    def rapport(self, request, pk=None):
        """Rapport détaillé de l'exercice : global + par entrepôt + par produit."""
        import traceback
        from django.db.models import F, Sum, Count
        from collections import defaultdict
        try:
            exercice = self.get_object()
            boutiques = list(Boutique.objects.filter(entreprise=exercice.entreprise))
            if exercice.statut == 'cloture':
                return Response({'exercice': ExerciceFiscalSerializer(exercice).data, 'source': 'snapshot'})

            date_debut = exercice.date_debut
            date_fin = exercice.date_fin
            statuts_ca = ['Payé', 'Partiellement payé', 'En attente']

            factures_qs = Facture.objects.filter(
                boutique__in=boutiques,
                created_at__date__gte=date_debut,
                created_at__date__lte=date_fin,
                status__in=statuts_ca,
            )

            # ── Totaux globaux ──────────────────────────────────────────────────
            ca = factures_qs.aggregate(total=Sum('total'))['total'] or 0
            nb_factures = factures_qs.count()

            # Achats (mouvements entrée)
            total_achats = MouvementStock.objects.filter(
                entrepot__in=boutiques,
                type_mouvement='entree',
                created_at__date__gte=date_debut,
                created_at__date__lte=date_fin,
            ).aggregate(total=Sum(F('quantite') * F('produit__prix_achat')))['total'] or 0

            # Stock actuel
            stocks_qs = Stock.objects.filter(entrepot__in=boutiques).select_related('produit', 'entrepot')
            valeur_stock = sum(
                (s.quantite or 0) * float(s.produit.prix_vente or s.produit.prix or 0)
                for s in stocks_qs
            )
            nb_produits = Produit.objects.filter(entreprise=exercice.entreprise, actif=True).count()

            # ── Par entrepôt ────────────────────────────────────────────────────
            par_entrepot = []
            for b in boutiques:
                f_b = factures_qs.filter(boutique=b)
                ca_b = f_b.aggregate(t=Sum('total'))['t'] or 0
                nb_b = f_b.count()
                achats_b = MouvementStock.objects.filter(
                    entrepot=b, type_mouvement='entree',
                    created_at__date__gte=date_debut,
                    created_at__date__lte=date_fin,
                ).aggregate(total=Sum(F('quantite') * F('produit__prix_achat')))['total'] or 0
                stock_b = sum(
                    (s.quantite or 0) * float(s.produit.prix_vente or s.produit.prix or 0)
                    for s in stocks_qs if s.entrepot_id == b.id
                )
                par_entrepot.append({
                    'nom': b.nom,
                    'ville': b.ville or '',
                    'ca': float(ca_b),
                    'nb_factures': nb_b,
                    'total_achats': float(achats_b),
                    'benefice': float(ca_b) - float(achats_b),
                    'valeur_stock': float(stock_b),
                })

            # ── Par produit (lignes de commande dans les factures de la période) ─
            produit_agg = defaultdict(lambda: {'nom': '', 'reference': '', 'qte': 0, 'ca': 0.0, 'stock': 0})
            for cmd in CommandeClient.objects.filter(
                facture__in=factures_qs
            ).select_related('produit'):
                d = produit_agg[cmd.produit_id]
                d['nom'] = cmd.produit.nom
                d['reference'] = cmd.produit.reference or ''
                d['qte'] += cmd.quantite
                d['ca'] += cmd.quantite * float(cmd.prix_unitaire_fcfa)

            for cmd in CommandePartenaire.objects.filter(
                facture__in=factures_qs
            ).select_related('produit'):
                d = produit_agg[cmd.produit_id]
                d['nom'] = cmd.produit.nom
                d['reference'] = cmd.produit.reference or ''
                d['qte'] += cmd.quantite
                d['ca'] += cmd.quantite * float(cmd.prix_unitaire_fcfa)

            # Ajouter stock actuel par produit
            stock_par_produit = defaultdict(int)
            for s in stocks_qs:
                stock_par_produit[s.produit_id] += s.quantite or 0
            for pid, d in produit_agg.items():
                d['stock'] = stock_par_produit.get(pid, 0)

            par_produit = sorted(produit_agg.values(), key=lambda x: x['ca'], reverse=True)

            return Response({
                'exercice': ExerciceFiscalSerializer(exercice).data,
                'source': 'live',
                'chiffre_affaires': float(ca),
                'total_achats': float(total_achats),
                'nb_factures': nb_factures,
                'valeur_stock': float(valeur_stock),
                'nb_produits': nb_produits,
                'benefice_net': float(ca) - float(total_achats),
                'par_entrepot': par_entrepot,
                'par_produit': par_produit,
            })
        except Exception as exc:
            return Response({'error': str(exc), 'detail': traceback.format_exc()}, status=500)
