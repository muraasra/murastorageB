from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now  # Import this at the top
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
import uuid
import string
import random

def generate_entreprise_id():
    """Génère un ID unique de 10 caractères pour l'entreprise"""
    while True:
        # Génère un ID de 10 caractères alphanumériques
        entreprise_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        # Vérifie que l'ID n'existe pas déjà
        if not Entreprise.objects.filter(id_entreprise=entreprise_id).exists():
            return entreprise_id

class Entreprise(models.Model):
    """Modèle pour représenter une entreprise"""
    id_entreprise = models.CharField(
        max_length=10, 
        unique=True, 
        default=generate_entreprise_id,
        help_text="ID unique de 10 caractères pour identifier l'entreprise"
    )
    nom = models.CharField(max_length=200, help_text="Nom de l'entreprise")
    description = models.TextField(blank=True, help_text="Description de l'entreprise")
    secteur_activite = models.CharField(max_length=100, help_text="Secteur d'activité")
    logo = models.ImageField(upload_to='entreprises/logos/', blank=True, null=True, help_text="Logo de l'entreprise")
    
    # Informations de contact
    adresse = models.TextField(help_text="Adresse complète")
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20, blank=True)
    pays = models.CharField(max_length=100, default="Cameroun")
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(help_text="Email de contact de l'entreprise")
    site_web = models.URLField(blank=True, help_text="Site web de l'entreprise")
    
    # Informations légales
    numero_fiscal = models.CharField(max_length=50, blank=True, help_text="Numéro fiscal")
    nombre_employes = models.IntegerField(default=0, help_text="Nombre d'employés")
    annee_creation = models.IntegerField(help_text="Année de création")
    
    # Informations du pack
    pack_type = models.CharField(
        max_length=20,
        choices=[
            ('basique', 'Basique'),
            ('professionnel', 'Professionnel'),
            ('entreprise', 'Entreprise'),
        ],
        default='basique'
    )
    pack_prix = models.FloatField(default=0)
    pack_duree = models.CharField(max_length=20, default='mensuel')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.nom} ({self.id_entreprise})"

class Boutique(models.Model):
    """Modèle pour représenter un entrepôt/boutique d'une entreprise"""
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='boutiques', null=True, blank=True)
    ville = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    adresse = models.TextField(blank=True, help_text="Adresse de l'entrepôt")
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    responsable = models.CharField(max_length=100, blank=True, help_text="Nom du responsable")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'Boutique/Entrepôt'
        verbose_name_plural = 'Boutiques/Entrepôts'
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['nom']),
            models.Index(fields=['ville']),
            models.Index(fields=['is_active']),
            models.Index(fields=['entreprise', 'is_active']),
        ]

    def __str__(self):
        return f"{self.nom} - {self.entreprise.nom}" if self.entreprise else self.nom

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('superadmin', 'SuperAdmin'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    boutique = models.ForeignKey(Boutique, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    # Informations personnelles supplémentaires
    telephone = models.CharField(max_length=20, blank=True)
    poste = models.CharField(max_length=100, blank=True, help_text="Poste occupé dans l'entreprise")
    date_embauche = models.DateField(null=True, blank=True)
    is_active_employee = models.BooleanField(default=True, help_text="L'employé est-il actif ?")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['boutique']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['entreprise', 'is_active']),
            models.Index(fields=['boutique', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    def save(self, *args, **kwargs):
        # Les superadmins peuvent être associés à une entreprise
        super().save(*args, **kwargs)

class Categorie(models.Model):
    """Modèle pour les catégories de produits"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sous_categories')
    icone = models.CharField(max_length=50, blank=True, help_text="Classe CSS pour l'icône")
    couleur = models.CharField(max_length=7, default='#3B82F6', help_text="Code couleur hexadécimal")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='categories')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent.nom} > {self.nom}" if self.parent else self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['nom']),
            models.Index(fields=['actif']),
            models.Index(fields=['entreprise', 'actif']),
        ]

class Fournisseur(models.Model):
    """Modèle pour les fournisseurs"""
    nom = models.CharField(max_length=200)
    code_fournisseur = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Informations de contact
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default="Cameroun")
    
    # Informations commerciales
    delai_livraison_jours = models.IntegerField(default=7, help_text="Délai de livraison moyen en jours")
    conditions_paiement = models.CharField(max_length=100, blank=True)
    remise_defaut = models.FloatField(default=0, help_text="Remise par défaut en %")
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='fournisseurs')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['nom']),
            models.Index(fields=['code_fournisseur']),
            models.Index(fields=['actif']),
            models.Index(fields=['entreprise', 'actif']),
        ]

class Produit(models.Model):
    """Modèle optimisé pour les produits - Version simplifiée"""
    
    # 1. Identification essentielle
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Code produit unique (SKU)")
    nom = models.CharField(max_length=200, help_text="Nom du produit")
    description = models.TextField(blank=True, help_text="Description du produit")
    code_barres = models.CharField(max_length=50, blank=True, unique=True, null=True, help_text="Code-barres")
    
    # Relations essentielles
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='produits', null=True, blank=True)
    fournisseur_principal = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    
    # Image
    image = models.ImageField(upload_to='produits/images/', blank=True, null=True, help_text="Image du produit")
    
    # 2. Informations commerciales essentielles
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Prix d'achat unitaire")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Prix de vente unitaire")
    prix_gros = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix de gros")
    
    # Devise
    devise = models.CharField(max_length=3, default='XAF', choices=[
        ('XAF', 'Franc CFA'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar US'),
    ])
    
    # 3. Gestion des stocks essentielle
    unite_mesure = models.CharField(max_length=20, default='piece', choices=[
        ('piece', 'Pièce'),
        ('kg', 'Kilogramme'),
        ('g', 'Gramme'),
        ('l', 'Litre'),
        ('ml', 'Millilitre'),
        ('m', 'Mètre'),
        ('cm', 'Centimètre'),
        ('carton', 'Carton'),
        ('paquet', 'Paquet'),
    ])
    
    # Seuils de stock essentiels
    stock_minimum = models.IntegerField(default=0, help_text="Seuil d'alerte minimum")
    stock_maximum = models.IntegerField(default=1000, help_text="Stock maximum recommandé")
    
    # État du produit
    etat_produit = models.CharField(max_length=20, default='neuf', choices=[
        ('neuf', 'Neuf'),
        ('occasion', 'Occasion'),
        ('reconditionne', 'Reconditionné'),
        ('defectueux', 'Défectueux'),
    ])
    
    # Métadonnées
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Champs de compatibilité avec l'ancien système (simplifiés)
    reference = models.CharField(max_length=100, blank=True, help_text="Référence produit (compatibilité)")
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix de vente (compatibilité)")
    quantite = models.IntegerField(default=0, help_text="Quantité totale (calculée)")
    category = models.CharField(max_length=20, blank=True, help_text="Catégorie (compatibilité)")
    
    # Champs spécifiques aux ordinateurs (simplifiés - seulement les plus utiles)
    marque = models.CharField(max_length=100, blank=True, null=True, help_text="Marque du produit")
    modele = models.CharField(max_length=100, blank=True, null=True, help_text="Modèle du produit")
    specifications = models.JSONField(default=dict, blank=True, help_text="Spécifications techniques (JSON)")

    def save(self, *args, **kwargs):
        # Générer automatiquement le SKU s'il n'existe pas
        if not self.sku:
            self.sku = self.generate_sku()
        
        # Générer automatiquement le code-barres s'il n'existe pas
        if not self.code_barres:
            self.code_barres = self.generate_barcode()
        
        # Synchroniser les champs de compatibilité
        if not self.prix:
            self.prix = self.prix_vente
        if not self.reference:
            self.reference = self.sku
        if not self.category and self.categorie:
            self.category = self.categorie.nom.lower().replace(' ', '_')
        
        super().save(*args, **kwargs)
        
        # Mettre à jour la quantité totale
        self.update_total_quantity()

    def generate_sku(self):
        """Génère un SKU unique basé sur l'entreprise et un compteur"""
        if self.entreprise:
            # Format: ENT-XXXX-YYYY (ENT = code entreprise, XXXX = année, YYYY = compteur)
            year = timezone.now().year
            last_product = Produit.objects.filter(
                entreprise=self.entreprise,
                sku__startswith=f"{self.entreprise.id_entreprise}-{year}-"
            ).order_by('-sku').first()
            
            if last_product and last_product.sku:
                try:
                    counter = int(last_product.sku.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    counter = 1
            else:
                counter = 1
            
            return f"{self.entreprise.id_entreprise}-{year}-{counter:04d}"
        return f"PRD-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    def generate_barcode(self):
        """Génère un code-barres EAN-13 unique"""
        import random
        import time
        
        # Utiliser le timestamp pour garantir l'unicité
        timestamp = str(int(time.time()))[-8:]  # 8 derniers chiffres du timestamp
        
        # Générer un code-barres de 12 chiffres
        base_code = timestamp + ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Calculer le chiffre de contrôle EAN-13
        odd_sum = sum(int(base_code[i]) for i in range(0, 12, 2))
        even_sum = sum(int(base_code[i]) for i in range(1, 12, 2))
        check_digit = (10 - ((odd_sum + even_sum * 3) % 10)) % 10
        
        barcode = base_code + str(check_digit)
        
        # Vérifier l'unicité
        while Produit.objects.filter(code_barres=barcode).exists():
            base_code = timestamp + ''.join([str(random.randint(0, 9)) for _ in range(4)])
            odd_sum = sum(int(base_code[i]) for i in range(0, 12, 2))
            even_sum = sum(int(base_code[i]) for i in range(1, 12, 2))
            check_digit = (10 - ((odd_sum + even_sum * 3) % 10)) % 10
            barcode = base_code + str(check_digit)
        
        return barcode


    def update_total_quantity(self):
        """Met à jour la quantité totale basée sur les stocks des entrepôts"""
        total = self.stocks.aggregate(total=models.Sum('quantite'))['total'] or 0
        self.quantite = total
        # Sauvegarder sans déclencher save() pour éviter la récursion
        Produit.objects.filter(pk=self.pk).update(quantite=total)

    def get_marge(self):
        """Calcule la marge en pourcentage"""
        if self.prix_achat and self.prix_vente:
            return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100
        return 0

    def get_marge_absolue(self):
        """Calcule la marge absolue"""
        if self.prix_achat and self.prix_vente:
            return self.prix_vente - self.prix_achat
        return 0

    def is_stock_low(self):
        """Vérifie si le stock est en alerte"""
        return self.quantite <= self.stock_minimum

    def is_stock_high(self):
        """Vérifie si le stock dépasse le maximum"""
        return self.quantite >= self.stock_maximum

    def needs_reorder(self):
        """Vérifie si une commande est nécessaire"""
        return self.quantite <= self.point_commande

    def __str__(self):
        return f"{self.nom} ({self.sku})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['categorie']),
            models.Index(fields=['fournisseur_principal']),
            models.Index(fields=['nom']),
            models.Index(fields=['sku']),
            models.Index(fields=['actif']),
            models.Index(fields=['entreprise', 'actif']),
            models.Index(fields=['categorie', 'actif']),
            models.Index(fields=['entreprise', 'categorie']),
            models.Index(fields=['prix_vente']),
            models.Index(fields=['created_at']),
        ]

class Stock(models.Model):
    """Modèle pour la gestion des stocks par entrepôt"""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks')
    entrepot = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='stocks')
    quantite = models.IntegerField(default=0)
    quantite_reservee = models.IntegerField(default=0, help_text="Quantité réservée pour les commandes")
    emplacement = models.CharField(max_length=100, blank=True, help_text="Emplacement dans l'entrepôt")
    
    # Informations de traçabilité
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_quantite_disponible(self):
        """Retourne la quantité disponible (quantité - réservée)"""
        return max(0, self.quantite - self.quantite_reservee)
    
    def __str__(self):
        return f"{self.produit.nom} - {self.entrepot.nom} ({self.quantite})"
    
    class Meta:
        unique_together = ['produit', 'entrepot']
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        indexes = [
            models.Index(fields=['produit']),
            models.Index(fields=['entrepot']),
            models.Index(fields=['quantite']),
            models.Index(fields=['entrepot', 'quantite']),
            models.Index(fields=['produit', 'entrepot']),
            models.Index(fields=['updated_at']),
        ]

class MouvementStock(models.Model):
    """Modèle pour tracer tous les mouvements de stock"""
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('transfert', 'Transfert'),
        ('perte', 'Perte'),
        ('retour', 'Retour'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    entrepot = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    quantite_avant = models.IntegerField()
    quantite_apres = models.IntegerField()
    
    # Informations contextuelles
    reference_document = models.CharField(max_length=100, blank=True, help_text="Référence du document source")
    motif = models.TextField(blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mouvements_stock')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.produit.nom} ({self.quantite})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        indexes = [
            models.Index(fields=['produit']),
            models.Index(fields=['entrepot']),
            models.Index(fields=['type_mouvement']),
            models.Index(fields=['utilisateur']),
            models.Index(fields=['created_at']),
            models.Index(fields=['entrepot', 'created_at']),
            models.Index(fields=['produit', 'entrepot']),
        ]

class PrixProduit(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE)
    prix_achat_yen = models.FloatField()
    prix_vente_yen = models.FloatField()
    taux_fcfa = models.FloatField(default=1)
    date = models.DateTimeField(auto_now_add=True)

    def prix_vente_fcfa(self):
        return self.prix_vente_yen * self.taux_fcfa

class SequenceFacture(models.Model):
    """Modèle pour gérer les séquences de numérotation des factures par boutique"""
    boutique = models.OneToOneField(Boutique, on_delete=models.CASCADE, related_name='sequence_facture')
    annee = models.IntegerField()
    mois = models.IntegerField()
    dernier_numero = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['boutique', 'annee', 'mois']
        ordering = ['boutique', 'annee', 'mois']
    
    def __str__(self):
        return f"{self.boutique.nom} - {self.annee}/{self.mois:02d} - #{self.dernier_numero}"
    
    @classmethod
    def get_next_number(cls, boutique):
        """Obtenir le prochain numéro de facture pour une boutique"""
        from django.db import transaction
        from datetime import datetime
        
        now = datetime.now()
        annee = now.year
        mois = now.month
        
        with transaction.atomic():
            # Utiliser select_for_update pour éviter les conflits de concurrence
            sequence, created = cls.objects.select_for_update().get_or_create(
                boutique=boutique,
                annee=annee,
                mois=mois,
                defaults={'dernier_numero': 0}
            )
            
            sequence.dernier_numero += 1
            sequence.save()
            
            return sequence.dernier_numero
    
    @classmethod
    def generate_invoice_number(cls, boutique):
        """Générer un numéro de facture complet conforme aux normes françaises"""
        numero = cls.get_next_number(boutique)
        now = datetime.now()
        
        # Format: FA{ID_BOUTIQUE}-{YYMMDD}-{NNNN}
        # Exemple: FA7-251014-0013
        boutique_id = boutique.id if boutique else 1
        return f"FA{boutique_id}-{now.year % 100:02d}{now.month:02d}{now.day:02d}-{numero:04d}"

class Client(models.Model):
    """Modèle pour les clients de l'entreprise"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, default='')
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, default='Bafoussam')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='clients')
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='clients')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['telephone', 'entreprise']
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.telephone}"

class Partenaire(models.Model):
    choiceStatut = (
        ('encours','En Cours'),
        ('paye','Payé'),
    )
    
    nom = models.CharField(max_length=100)
    prenom =  models.CharField(max_length=100, default='')
    telephone = models.CharField(max_length=20,default=0)
    statut = models.CharField(max_length=20, choices=choiceStatut,default='encours')
    boutique = models.BooleanField(default=True)
    localisation = models.CharField(max_length=100, default='Bafoussam')
    dateadhesion = models.DateTimeField(default=now)

class Facture(models.Model):
    TYPES = (
        ('client', 'Client'),
        ('partenaire', 'Partenaire'),
    )
    STATUS_CHOICES = (
        ('En attente', 'En attente'),
        ('Payé', 'Payé'),
        ('Partiellement payé', 'Partiellement payé'),
        ('Annulé', 'Annulé'),
    )
    
    type = models.CharField(max_length=20, choices=TYPES)
    numero = models.CharField(max_length=50, unique=True)
    total = models.FloatField()
    reste = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En attente')
    
    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='factures')
    partenaire = models.ForeignKey(Partenaire, on_delete=models.CASCADE, null=True, blank=True, related_name='factures')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='factures', null=True, blank=True)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='factures')
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['boutique']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['boutique', 'created_at']),
            models.Index(fields=['entreprise', 'created_at']),
        ]
    
    def __str__(self):
        destinataire = self.client if self.type == 'client' else self.partenaire
        return f"Facture {self.numero} - {destinataire}"
    
    def save(self, *args, **kwargs):
        """Sauvegarder la facture avec génération automatique du numéro"""
        if not self.numero:
            self.numero = SequenceFacture.generate_invoice_number(self.boutique)
        self.clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation: soit client soit partenaire doit être défini selon le type"""
        if self.type == 'client' and not self.client:
            raise ValidationError("Un client doit être spécifié pour une facture client")
        if self.type == 'partenaire' and not self.partenaire:
            raise ValidationError("Un partenaire doit être spécifié pour une facture partenaire")

class CommandeClient(models.Model):
    """Commande pour un client"""
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='commandes_client')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire_fcfa = models.FloatField()
    prix_initial_fcfa = models.FloatField(null=True, blank=True)  # Prix initial avant modification
    justification_prix = models.TextField(blank=True)  # Justification si le prix a été modifié
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def total(self):
        return self.quantite * self.prix_unitaire_fcfa
    
    def __str__(self):
        return f"Commande {self.facture.numero} - {self.produit.nom} x{self.quantite}"

class CommandePartenaire(models.Model):
    """Commande pour un partenaire"""
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='commandes_partenaire')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire_fcfa = models.FloatField()
    prix_initial_fcfa = models.FloatField(null=True, blank=True)  # Prix initial avant modification
    justification_prix = models.TextField(blank=True)  # Justification si le prix a été modifié
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def total(self):
        return self.quantite * self.prix_unitaire_fcfa
    
    def __str__(self):
        return f"Commande {self.facture.numero} - {self.produit.nom} x{self.quantite}"

class Versement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='versements')
    montant = models.FloatField()
    date_versement = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='versements_crees', null=True, blank=True)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='versements', null=True, blank=True)
    
    class Meta:
        ordering = ['-date_versement']
        verbose_name = "Versement"
        verbose_name_plural = "Versements"
    
    def __str__(self):
        return f"Versement {self.montant} XAF - Facture {self.facture.numero}"

class HistoriqueStock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    variation = models.IntegerField()
    motif = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

class Journal(models.Model):
    OPERATION_TYPES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('vente', 'Vente'),
        ('achat', 'Achat'),
        ('retour', 'Retour'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, related_name='journaux')
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, null=True, blank=True, related_name='journaux')
    type_operation = models.CharField(max_length=20, choices=OPERATION_TYPES)
    description = models.TextField()
    details = models.JSONField(null=True, blank=True)
    date_operation = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-date_operation']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journaux'
        indexes = [
            models.Index(fields=['date_operation']),
            models.Index(fields=['type_operation']),
            models.Index(fields=['utilisateur']),
            models.Index(fields=['boutique']),
        ]

    def __str__(self):
        return f"{self.utilisateur.username} - {self.type_operation} - {self.date_operation}"

    def save(self, *args, **kwargs):
        if not self.date_operation:
            self.date_operation = timezone.now()
        super().save(*args, **kwargs)

class SubscriptionPlan(models.Model):
    """Modèle pour définir les plans d'abonnement"""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('organisation', 'Organisation'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Limitations par plan
    max_entreprises = models.IntegerField(default=1)
    max_boutiques = models.IntegerField(default=1)
    max_users = models.IntegerField(default=2)
    max_produits = models.IntegerField(default=50, null=True, blank=True)  # null = illimité
    max_factures_per_month = models.IntegerField(default=100, null=True, blank=True)  # null = illimité
    
    # Fonctionnalités
    allow_export_csv = models.BooleanField(default=False)
    allow_export_excel = models.BooleanField(default=False)
    allow_import_csv = models.BooleanField(default=False)
    allow_api_access = models.BooleanField(default=False)
    allow_multiple_entreprises = models.BooleanField(default=False)
    allow_advanced_analytics = models.BooleanField(default=False)
    allow_custom_branding = models.BooleanField(default=False)
    
    # Support
    support_level = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('priority', 'Prioritaire'),
        ('dedicated', 'Dédié'),
    ], default='email')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price_monthly']
        verbose_name = 'Plan d\'abonnement'
        verbose_name_plural = 'Plans d\'abonnement'
    
    def __str__(self):
        return f"{self.display_name} - {self.price_monthly} XAF/mois"
    
    def is_unlimited(self, field_name):
        """Vérifier si un champ est illimité"""
        value = getattr(self, field_name, None)
        return value is None

class EntrepriseSubscription(models.Model):
    """Modèle pour gérer les abonnements des entreprises"""
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
        ('suspended', 'Suspendu'),
    ]
    
    entreprise = models.OneToOneField(Entreprise, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Dates importantes
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Informations de paiement
    payment_method = models.CharField(max_length=50, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Abonnement Entreprise'
        verbose_name_plural = 'Abonnements Entreprise'
    
    def __str__(self):
        return f"{self.entreprise.nom} - {self.plan.display_name}"
    
    def is_active(self):
        """Vérifier si l'abonnement est actif"""
        if self.status != 'active':
            return False
        
        if self.end_date and timezone.now() > self.end_date:
            return False
        
        return True
    
    def is_trial_active(self):
        """Vérifier si la période d'essai est active"""
        if not self.trial_end_date:
            return False
        return timezone.now() <= self.trial_end_date
    
    def get_remaining_trial_days(self):
        """Obtenir le nombre de jours restants de la période d'essai"""
        if not self.is_trial_active():
            return 0
        delta = self.trial_end_date - timezone.now()
        return delta.days

class UsageTracking(models.Model):
    """Modèle pour suivre l'utilisation des ressources par entreprise"""
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='usage_tracking')
    
    # Compteurs mensuels
    current_month = models.DateField(default=timezone.now().date().replace(day=1))
    factures_count = models.IntegerField(default=0)
    produits_count = models.IntegerField(default=0)
    users_count = models.IntegerField(default=0)
    boutiques_count = models.IntegerField(default=0)
    
    # Compteurs totaux
    total_factures = models.IntegerField(default=0)
    total_produits = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_boutiques = models.IntegerField(default=0)
    
    # Dernière mise à jour
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['entreprise', 'current_month']
        ordering = ['-current_month']
        verbose_name = 'Suivi d\'utilisation'
        verbose_name_plural = 'Suivi d\'utilisation'
    
    def __str__(self):
        return f"{self.entreprise.nom} - {self.current_month}"
    
    def reset_monthly_counters(self):
        """Réinitialiser les compteurs mensuels"""
        self.factures_count = 0
        self.current_month = timezone.now().date().replace(day=1)
        self.save()
    
    def increment_facture_count(self):
        """Incrémenter le compteur de factures"""
        self.factures_count += 1
        self.total_factures += 1
        self.save()
    
    def increment_produit_count(self):
        """Incrémenter le compteur de produits"""
        self.produits_count += 1
        self.total_produits += 1
        self.save()
    
    def update_users_count(self, count):
        """Mettre à jour le compteur d'utilisateurs"""
        self.users_count = count
        self.total_users = count
        self.save()
    
    def update_boutiques_count(self, count):
        """Mettre à jour le compteur de boutiques"""
        self.boutiques_count = count
        self.total_boutiques = count
        self.save()

class EmailVerification(models.Model):
    """Modèle pour gérer la vérification d'email lors de l'inscription"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('verified', 'Vérifié'),
        ('expired', 'Expiré'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    email = models.EmailField(help_text="Email à vérifier")
    verification_code = models.CharField(max_length=6, help_text="Code de vérification à 6 chiffres")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text="Date d'expiration du code")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vérification Email'
        verbose_name_plural = 'Vérifications Email'
    
    def __str__(self):
        return f"Vérification {self.email} - {self.status}"
    
    def is_expired(self):
        """Vérifier si le code a expiré"""
        return timezone.now() > self.expires_at
    
    def mark_as_verified(self):
        """Marquer comme vérifié"""
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.save()
    
    def mark_as_expired(self):
        """Marquer comme expiré"""
        self.status = 'expired'
        self.save()