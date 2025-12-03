from django.contrib import admin
from .models import (
    Entreprise, Boutique, User, Categorie, Fournisseur, Produit, Stock,
    MouvementStock, PrixProduit, SequenceFacture, Client, Partenaire,
    Facture, CommandeClient, CommandePartenaire, Versement, HistoriqueStock,
    Journal, SubscriptionPlan, EntrepriseSubscription, UsageTracking,
    EmailVerification, Inventaire, InventaireProduit
)

# Enregistrement de tous les modèles dans Django Admin

# Modèles principaux
admin.site.register(Entreprise)
admin.site.register(Boutique)
admin.site.register(User)
admin.site.register(Categorie)
admin.site.register(Fournisseur)

# Modèles produits et stocks
admin.site.register(Produit)
admin.site.register(Stock)
admin.site.register(MouvementStock)
admin.site.register(PrixProduit)

# Modèles facturation
admin.site.register(Client)
admin.site.register(Partenaire)
admin.site.register(Facture)
admin.site.register(SequenceFacture)
admin.site.register(CommandeClient)
admin.site.register(CommandePartenaire)
admin.site.register(Versement)

# Modèles inventaire
admin.site.register(Inventaire)
admin.site.register(InventaireProduit)

# Modèles système
admin.site.register(Journal)
admin.site.register(HistoriqueStock)

# Modèles abonnement
admin.site.register(SubscriptionPlan)
admin.site.register(EntrepriseSubscription)
admin.site.register(UsageTracking)

# Modèles authentification
admin.site.register(EmailVerification)