#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import Stock, Produit, Boutique

def create_test_stocks():
    print("Création de stocks de test...")
    
    # Récupérer les produits et boutiques
    produits = list(Produit.objects.all()[:4])
    boutiques = list(Boutique.objects.all()[:3])
    
    print(f"Produits trouvés: {len(produits)}")
    print(f"Boutiques trouvées: {len(boutiques)}")
    
    stocks_created = 0
    
    # Créer des stocks pour chaque produit dans différentes boutiques
    for i, produit in enumerate(produits):
        for j, boutique in enumerate(boutiques):
            try:
                # Éviter les doublons
                if Stock.objects.filter(produit=produit, entrepot=boutique).exists():
                    print(f"Stock existe déjà: {produit.nom} - {boutique.nom}")
                    continue
                
                quantite = 10 + (i * 5) + (j * 3)
                stock = Stock.objects.create(
                    produit=produit,
                    entrepot=boutique,
                    quantite=quantite,
                    emplacement=f"Rangée {i+1}, Étagère {j+1}"
                )
                print(f"Stock créé: {produit.nom} - {boutique.nom} ({quantite})")
                stocks_created += 1
                
            except Exception as e:
                print(f"Erreur lors de la création du stock: {e}")
    
    print(f"Total des stocks créés: {stocks_created}")
    print(f"Total des stocks dans la base: {Stock.objects.count()}")
    
    # Afficher tous les stocks
    print("\nStocks existants:")
    for stock in Stock.objects.all():
        print(f"- {stock.produit.nom} - {stock.entrepot.nom}: {stock.quantite}")

if __name__ == "__main__":
    create_test_stocks()
