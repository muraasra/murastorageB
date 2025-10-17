from django.contrib import admin
from .models import Boutique, User, Produit, PrixProduit, Partenaire, Facture, CommandeClient, CommandePartenaire, Versement, HistoriqueStock

# Enregistrement simple
admin.site.register(Boutique)
admin.site.register(User)
admin.site.register(Produit)
admin.site.register(PrixProduit)
admin.site.register(Partenaire)
admin.site.register(Facture)
admin.site.register(CommandeClient)
admin.site.register(CommandePartenaire)
admin.site.register(Versement)
admin.site.register(HistoriqueStock)