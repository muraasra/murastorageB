from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *

User = get_user_model()

class EntrepriseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Entreprise"""
    class Meta:
        model = Entreprise
        fields = '__all__'
        read_only_fields = ('id_entreprise', 'created_at', 'updated_at')
    
    def validate_annee_creation(self, value):
        """Valider l'année de création"""
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError(
                f"L'année de création doit être entre 1900 et {current_year}"
            )
        return value
    
    def validate_nombre_employes(self, value):
        """Valider le nombre d'employés"""
        if value < 0:
            raise serializers.ValidationError("Le nombre d'employés ne peut pas être négatif")
        return value

class InscriptionUserSerializer(serializers.Serializer):
    """Sérialiseur pour les données utilisateur lors de l'inscription"""
    nom = serializers.CharField(max_length=150, help_text="Nom de l'utilisateur")
    prenom = serializers.CharField(max_length=150, help_text="Prénom de l'utilisateur")
    email = serializers.EmailField(help_text="Email de l'utilisateur")
    telephone = serializers.CharField(max_length=20, help_text="Téléphone de l'utilisateur")
    mot_de_passe = serializers.CharField(min_length=8, write_only=True, help_text="Mot de passe (minimum 8 caractères)")
    role = serializers.CharField(default='superadmin', help_text="Rôle de l'utilisateur")

class EntrepriseCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur spécialisé pour la création d'entreprise avec utilisateur"""
    user = InscriptionUserSerializer(write_only=True, help_text="Données de l'utilisateur SuperAdmin")
    nom = serializers.CharField(max_length=200, help_text="Nom de l'entreprise")
    description = serializers.CharField(required=False, allow_blank=True, help_text="Description de l'entreprise")
    secteur_activite = serializers.CharField(max_length=100, help_text="Secteur d'activité de l'entreprise")
    adresse = serializers.CharField(help_text="Adresse complète de l'entreprise")
    ville = serializers.CharField(max_length=100, help_text="Ville de l'entreprise")
    code_postal = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text="Code postal")
    pays = serializers.CharField(max_length=100, default="Cameroun", help_text="Pays de l'entreprise")
    telephone = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text="Téléphone de l'entreprise")
    email = serializers.EmailField(help_text="Email de contact de l'entreprise")
    site_web = serializers.URLField(required=False, allow_blank=True, help_text="Site web de l'entreprise")
    numero_fiscal = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="Numéro fiscal")
    nombre_employes = serializers.IntegerField(default=0, help_text="Nombre d'employés")
    annee_creation = serializers.IntegerField(help_text="Année de création de l'entreprise")
    pack_type = serializers.ChoiceField(choices=[('basique', 'Basique'), ('professionnel', 'Professionnel'), ('entreprise', 'Entreprise')], default='basique', help_text="Type de pack")
    pack_prix = serializers.FloatField(default=0, help_text="Prix du pack")
    pack_duree = serializers.CharField(max_length=20, default='mensuel', help_text="Durée du pack")
    is_active = serializers.BooleanField(default=True, help_text="Statut actif de l'entreprise")
    
    class Meta:
        model = Entreprise
        fields = [
            'user', 'nom', 'description', 'secteur_activite', 'adresse', 'ville', 
            'code_postal', 'pays', 'telephone', 'email', 'site_web', 'numero_fiscal',
            'nombre_employes', 'annee_creation', 'pack_type', 'pack_prix', 'pack_duree', 'is_active'
        ]
        read_only_fields = ('id_entreprise', 'created_at', 'updated_at')
    
    def validate_annee_creation(self, value):
        """Valider l'année de création"""
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError(
                f"L'année de création doit être entre 1900 et {current_year}"
            )
        return value
    
    def validate_nombre_employes(self, value):
        """Valider le nombre d'employés"""
        if value < 0:
            raise serializers.ValidationError("Le nombre d'employés ne peut pas être négatif")
        return value
    
    def validate_user(self, value):
        """Valider les données utilisateur"""
        if not value.get('email'):
            raise serializers.ValidationError("L'email utilisateur est requis")
        if not value.get('mot_de_passe'):
            raise serializers.ValidationError("Le mot de passe utilisateur est requis")
        if len(value.get('mot_de_passe', '')) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères")
        return value
    
    def create(self, validated_data):
        from .utils import send_verification_email
        
        user_data = validated_data.pop('user')
        
        # Créer l'entreprise
        entreprise = Entreprise.objects.create(**validated_data)
        
        # Créer l'utilisateur superadmin
        user = User.objects.create_user(
            username=user_data['email'],  # Utiliser l'email comme username
            email=user_data['email'],
            first_name=user_data['nom'],
            last_name=user_data['prenom'],
            password=user_data['mot_de_passe'],
            telephone=user_data['telephone'],
            role='superadmin',
            entreprise=entreprise,
            poste='Super Administrateur'
        )
        
        # Créer un entrepôt par défaut
        boutique_default = Boutique.objects.create(
            entreprise=entreprise,
            nom=f"Entrepôt Principal - {entreprise.nom}",
            ville=entreprise.ville,
            adresse=entreprise.adresse,
            telephone=entreprise.telephone,
            email=entreprise.email,
            responsable=f"{user.first_name} {user.last_name}"
        )
        
        # Assigner l'entrepôt par défaut à l'utilisateur
        user.boutique = boutique_default
        user.save()
        
        # Envoyer l'email de vérification
        email_sent, result = send_verification_email(user, entreprise)
        
        if not email_sent:
            # Si l'email n'a pas pu être envoyé, on peut logger l'erreur
            # mais on ne fait pas échouer la création de l'entreprise
            print(f"Erreur lors de l'envoi de l'email de vérification: {result}")
        
        return entreprise

class InscriptionResponseSerializer(serializers.Serializer):
    """Sérialiseur pour la réponse d'inscription"""
    success = serializers.BooleanField(help_text="Indique si l'inscription a réussi")
    message = serializers.CharField(help_text="Message de confirmation ou d'erreur")
    entreprise = EntrepriseSerializer(help_text="Données de l'entreprise créée")

class BoutiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boutique
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    entreprise_nom = serializers.SerializerMethodField()
    boutique_nom = serializers.SerializerMethodField()
    entreprise_data = serializers.SerializerMethodField()
    boutique_data = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 
            'entreprise', 'boutique', 'telephone', 'poste', 'date_embauche', 
            'is_active_employee', 'created_at', 'updated_at',
            'entreprise_nom', 'boutique_nom', 'entreprise_data', 'boutique_data'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_entreprise_nom(self, obj):
        return obj.entreprise.nom if obj.entreprise else None
    
    def get_boutique_nom(self, obj):
        return obj.boutique.nom if obj.boutique else None
    
    def get_entreprise_data(self, obj):
        if obj.entreprise:
            return {
                'id': obj.entreprise.id,
                'nom': obj.entreprise.nom,
                'id_entreprise': obj.entreprise.id_entreprise,
                'logo': obj.entreprise.logo.url if obj.entreprise.logo else None
            }
        return None
    
    def get_boutique_data(self, obj):
        if obj.boutique:
            return {
                'id': obj.boutique.id,
                'nom': obj.boutique.nom,
                'ville': obj.boutique.ville,
                'adresse': obj.boutique.adresse,
                'telephone': obj.boutique.telephone,
                'email': obj.boutique.email,
                'responsable': obj.boutique.responsable
            }
        return None

class EmailVerificationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la vérification d'email"""
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailVerification
        fields = ['id', 'email', 'verification_code', 'status', 'created_at', 'expires_at', 'verified_at', 'is_expired']
        read_only_fields = ['id', 'created_at', 'expires_at', 'verified_at']
    
    def get_is_expired(self, obj):
        return obj.is_expired()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer JWT personnalisé qui permet l'authentification par email et retourne le maximum d'informations utilisateur"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permettre l'authentification par email
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
    
    def validate(self, attrs):
        # Récupérer username ou email
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
            # Utiliser le username fourni
            username = username
        
        # Authentifier avec le username trouvé
        attrs['username'] = username
        data = super().validate(attrs)
        
        # Ajouter des informations supplémentaires à la réponse
        user = self.user
        
        # Informations utilisateur de base
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'role': user.role,
            'telephone': user.telephone or '',
            'poste': user.poste or '',
            'is_active_employee': user.is_active_employee,
        }
        
        # Informations entreprise
        entreprise_data = None
        if user.entreprise:
            entreprise_data = {
                'id': user.entreprise.id,
                'id_entreprise': user.entreprise.id_entreprise,
                'nom': user.entreprise.nom,
                'secteur_activite': user.entreprise.secteur_activite,
                'ville': user.entreprise.ville,
                'pack_type': user.entreprise.pack_type,
                'nombre_employes': user.entreprise.nombre_employes,
                'annee_creation': user.entreprise.annee_creation,
            }
        
        # Informations boutique
        boutique_data = None
        if user.boutique:
            boutique_data = {
                'id': user.boutique.id,
                'nom': user.boutique.nom,
                'ville': user.boutique.ville or '',
                'responsable': user.boutique.responsable or '',
            }
        
        # Permissions utilisateur
        permissions = {
            'can_create_produits': user.role in ['admin', 'superadmin'],
            'can_create_factures': user.role in ['admin', 'superadmin'],
            'can_manage_users': user.role == 'superadmin',
            'can_manage_entreprises': user.role == 'superadmin',
            'can_view_reports': user.role in ['admin', 'superadmin'],
            'can_manage_boutiques': user.role in ['admin', 'superadmin'],
        }
        
        # Ajouter toutes les informations à la réponse
        data.update({
            'user': user_data,
            'entreprise': entreprise_data,
            'boutique': boutique_data,
            'permissions': permissions,
            'message': 'Connexion réussie avec JWT',
            'success': True,
        })
        
        return data

class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer un nouvel utilisateur dans une entreprise"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password',
            'role', 'entreprise', 'boutique', 'telephone', 'poste', 'date_embauche'
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CategorieSerializer(serializers.ModelSerializer):
    sous_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = '__all__'
    
    def get_sous_categories(self, obj):
        if obj.sous_categories.exists():
            return CategorieSerializer(obj.sous_categories.all(), many=True).data
        return []

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    quantite_disponible = serializers.ReadOnlyField()
    
    class Meta:
        model = Stock
        fields = '__all__'

class MouvementStockSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.get_full_name', read_only=True)
    
    class Meta:
        model = MouvementStock
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour les produits"""
    
    # Relations
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    fournisseur_nom = serializers.CharField(source='fournisseur_principal.nom', read_only=True)
    
    # Calculs automatiques
    marge = serializers.SerializerMethodField()
    marge_absolue = serializers.SerializerMethodField()
    stock_low = serializers.SerializerMethodField()
    stock_high = serializers.SerializerMethodField()
    
    # Stocks par entrepôt
    stocks = StockSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produit
        fields = '__all__'
        extra_kwargs = {
            'sku': {'required': False},
            'code_barres': {'required': False},
            'image': {'required': False},
            'prix_gros': {'required': False},
            'marque': {'required': False, 'allow_null': True},
            'modele': {'required': False, 'allow_null': True},
            'specifications': {'required': False},
            'reference': {'required': False},
            'description': {'required': False},
            'prix_achat': {'required': True},
            'prix_vente': {'required': True},
            'quantite': {'required': False},
            'entreprise': {'required': True},
            'nom': {'required': True}
        }
    
    def get_marge(self, obj):
        return obj.get_marge()
    
    def get_marge_absolue(self, obj):
        return obj.get_marge_absolue()
    
    def get_stock_low(self, obj):
        return obj.is_stock_low()
    
    def get_stock_high(self, obj):
        return obj.is_stock_high()

    def validate(self, data):
        """Validation des données du produit"""
        # Vérifier que le prix de vente est supérieur au prix d'achat
        if data.get('prix_achat', 0) > 0 and data.get('prix_vente', 0) > 0:
            if data['prix_vente'] <= data['prix_achat']:
                raise serializers.ValidationError(
                    "Le prix de vente doit être supérieur au prix d'achat"
                )
        
        # Gérer les spécifications pour les ordinateurs
        if data.get('category') == 'ordinateur' and 'specifications' not in data:
            data['specifications'] = {}
        
        return data

    def create(self, validated_data):
        """Création d'un produit avec gestion des spécifications"""
        # Extraire les spécifications si elles existent
        specifications = validated_data.pop('specifications', {})
        
        # Créer le produit
        produit = super().create(validated_data)
        
        # Ajouter les spécifications
        if specifications:
            produit.specifications = specifications
            produit.save()
        
        return produit

    def update(self, instance, validated_data):
        """Mise à jour d'un produit avec gestion des spécifications"""
        # Extraire les spécifications si elles existent
        specifications = validated_data.pop('specifications', None)
        
        # Mettre à jour le produit
        produit = super().update(instance, validated_data)
        
        # Mettre à jour les spécifications si fournies
        if specifications is not None:
            produit.specifications = specifications
            produit.save()
        
        return produit

class PrixProduitSerializer(serializers.ModelSerializer):
    prix_vente_fcfa = serializers.FloatField(read_only=True)

    class Meta:
        model = PrixProduit
        fields = '__all__'

class PartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = '__all__'

class SequenceFactureSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle SequenceFacture"""
    boutique_nom = serializers.CharField(source='boutique.nom', read_only=True)
    
    class Meta:
        model = SequenceFacture
        fields = ['id', 'boutique', 'boutique_nom', 'annee', 'mois', 'dernier_numero', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClientSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Client"""
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ['id', 'nom', 'prenom', 'nom_complet', 'telephone', 'email', 'adresse', 
                 'ville', 'entreprise', 'boutique', 'date_creation', 'date_modification', 'actif']
        read_only_fields = ['id', 'date_creation', 'date_modification']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}".strip()
    
    def validate_telephone(self, value):
        """Valider l'unicité du téléphone par entreprise"""
        if self.instance:
            # Mode édition
            if Client.objects.filter(telephone=value, entreprise=self.instance.entreprise).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ce numéro de téléphone existe déjà pour cette entreprise")
        else:
            # Mode création
            entreprise = self.initial_data.get('entreprise')
            if entreprise and Client.objects.filter(telephone=value, entreprise=entreprise).exists():
                raise serializers.ValidationError("Ce numéro de téléphone existe déjà pour cette entreprise")
        return value

class FactureSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Facture"""
    client_nom = serializers.SerializerMethodField()
    partenaire_nom = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    boutique_nom = serializers.CharField(source='boutique.nom', read_only=True)
    
    def get_client_nom(self, obj):
        """Récupérer le nom complet du client"""
        if obj.client:
            return f"{obj.client.prenom} {obj.client.nom}".strip()
        return None
    
    def get_partenaire_nom(self, obj):
        """Récupérer le nom du partenaire"""
        if obj.partenaire:
            return str(obj.partenaire)
        return None
    
    class Meta:
        model = Facture
        fields = ['id', 'type', 'numero', 'total', 'reste', 'status', 'client', 'partenaire',
                 'client_nom', 'partenaire_nom', 'created_by', 'created_by_username',
                 'entreprise', 'boutique', 'boutique_nom', 'created_at', 'updated_at']
        read_only_fields = ['id', 'numero', 'created_at', 'updated_at']
        extra_kwargs = {
            'numero': {'required': False}  # Le numéro sera généré automatiquement
        }
    
    def validate(self, data):
        """Validation personnalisée"""
        if data.get('type') == 'client' and not data.get('client'):
            raise serializers.ValidationError("Un client doit être spécifié pour une facture client")
        if data.get('type') == 'partenaire' and not data.get('partenaire'):
            raise serializers.ValidationError("Un partenaire doit être spécifié pour une facture partenaire")
        return data

class CommandeClientSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle CommandeClient"""
    total = serializers.ReadOnlyField()
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)
    
    class Meta:
        model = CommandeClient
        fields = ['id', 'facture', 'produit', 'produit_nom', 'produit_reference',
                 'quantite', 'prix_unitaire_fcfa', 'prix_initial_fcfa', 'justification_prix', 
                 'total', 'created_at']
        read_only_fields = ['id', 'total', 'created_at']
        extra_kwargs = {
            'prix_initial_fcfa': {'required': False},
            'justification_prix': {'required': False}
        }
    
    def validate(self, data):
        # Récupérer le produit pour vérifier le prix d'achat
        produit = data.get('produit')
        if produit:
            try:
                prix_achat = produit.prix_achat or 0
                prix_vente = data.get('prix_unitaire_fcfa', 0)
                
                # Validation plus flexible : prix de vente doit être au moins égal au prix d'achat
                if prix_vente < prix_achat:
                    raise serializers.ValidationError(
                        f"Le prix de vente ({prix_vente} FCFA) ne peut pas être inférieur au prix d'achat ({prix_achat} FCFA)"
                    )
                    
                # Validation optionnelle de marge minimale (désactivée pour l'instant)
                # marge_minimale = 5000  # 5000 FCFA
                # if prix_vente < prix_achat + marge_minimale:
                #     raise serializers.ValidationError(
                #         f"Le prix de vente ({prix_vente} FCFA) doit être au moins {prix_achat + marge_minimale} FCFA "
                #         f"(prix d'achat: {prix_achat} FCFA + marge minimale: {marge_minimale} FCFA)"
                #     )
                    
            except Exception as e:
                raise serializers.ValidationError(f"Erreur lors de la validation du produit: {str(e)}")
        
        return data
    
    def create(self, validated_data):
        # Le produit est déjà dans validated_data, pas besoin de le pop
        # Sauvegarder le prix initial
        validated_data['prix_initial_fcfa'] = validated_data.get('prix_unitaire_fcfa')
        commande = CommandeClient.objects.create(**validated_data)
        return commande

class CommandePartenaireSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle CommandePartenaire"""
    total = serializers.ReadOnlyField()
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)
    
    class Meta:
        model = CommandePartenaire
        fields = ['id', 'facture', 'produit', 'produit_nom', 'produit_reference',
                 'quantite', 'prix_unitaire_fcfa', 'prix_initial_fcfa', 'justification_prix', 
                 'total', 'created_at']
        read_only_fields = ['id', 'total', 'created_at']
        extra_kwargs = {
            'prix_initial_fcfa': {'required': False},
            'justification_prix': {'required': False}
        }

    def validate(self, data):
        # Même validation que pour CommandeClientSerializer
        produit = data.get('produit')
        if produit:
            try:
                prix_achat = produit.prix_achat or 0
                prix_vente = data.get('prix_unitaire_fcfa', 0)
                
                # Validation plus flexible : prix de vente doit être au moins égal au prix d'achat
                if prix_vente < prix_achat:
                    raise serializers.ValidationError(
                        f"Le prix de vente ({prix_vente} FCFA) ne peut pas être inférieur au prix d'achat ({prix_achat} FCFA)"
                    )
                    
                # Validation optionnelle de marge minimale (désactivée pour l'instant)
                # marge_minimale = 5000  # 5000 FCFA
                # if prix_vente < prix_achat + marge_minimale:
                #     raise serializers.ValidationError(
                #         f"Le prix de vente ({prix_vente} FCFA) est trop bas. "
                #         f"Le prix minimum requis est {prix_achat + marge_minimale} FCFA."
                #     )
                    
            except Exception as e:
                raise serializers.ValidationError(f"Erreur lors de la validation du produit: {str(e)}")
        
        return data

    def create(self, validated_data):
        # Le produit est déjà dans validated_data, pas besoin de le pop
        # Sauvegarder le prix initial
        validated_data['prix_initial_fcfa'] = validated_data.get('prix_unitaire_fcfa')
        commande = CommandePartenaire.objects.create(**validated_data)
        return commande

class VersementSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    boutique_nom = serializers.CharField(source='boutique.nom', read_only=True)
    facture_numero = serializers.CharField(source='facture.numero', read_only=True)
    
    class Meta:
        model = Versement
        fields = ['id', 'facture', 'facture_numero', 'montant', 'date_versement', 
                 'created_by', 'created_by_username', 'boutique', 'boutique_nom']
        read_only_fields = ['id', 'date_versement']

class HistoriqueStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueStock
        fields = '__all__'

class JournalSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    boutique_nom = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = '__all__'
        read_only_fields = ('date_operation',)

    def get_utilisateur_nom(self, obj):
        return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}" if obj.utilisateur else obj.utilisateur.username

    def get_boutique_nom(self, obj):
        return obj.boutique.nom if obj.boutique else None