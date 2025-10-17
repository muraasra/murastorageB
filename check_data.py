# check_data.py
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User, Entreprise, Produit, Stock, Boutique

def check_data():
    print("🔍 VÉRIFICATION DES DONNÉES")
    print("=" * 40)
    
    # Compter les données
    print(f"📊 Entreprises: {Entreprise.objects.count()}")
    print(f"📊 Boutiques: {Boutique.objects.count()}")
    print(f"📊 Utilisateurs: {User.objects.count()}")
    print(f"📊 Produits: {Produit.objects.count()}")
    print(f"📊 Stocks: {Stock.objects.count()}")
    
    print("\n👥 UTILISATEURS:")
    users = User.objects.all()[:5]
    for user in users:
        entreprise_nom = user.entreprise.nom if user.entreprise else "Aucune"
        boutique_nom = user.boutique.nom if user.boutique else "Aucune"
        print(f"  - {user.username} ({user.email})")
        print(f"    Entreprise: {entreprise_nom}")
        print(f"    Boutique: {boutique_nom}")
        print(f"    Rôle: {user.role}")
        print()
    
    print("🏢 ENTREPRISES:")
    entreprises = Entreprise.objects.all()[:3]
    for entreprise in entreprises:
        print(f"  - {entreprise.nom} (ID: {entreprise.id_entreprise})")
        print(f"    Email: {entreprise.email}")
        print(f"    Actif: {entreprise.is_active}")
        print()
    
    print("📦 PRODUITS:")
    produits = Produit.objects.all()[:3]
    for produit in produits:
        entreprise_nom = produit.entreprise.nom if produit.entreprise else "Aucune"
        print(f"  - {produit.nom} (SKU: {produit.sku})")
        print(f"    Entreprise: {entreprise_nom}")
        print(f"    Prix: {produit.prix_vente} XAF")
        print(f"    Actif: {produit.actif}")
        print()
    
    print("📊 STOCKS:")
    stocks = Stock.objects.all()[:3]
    for stock in stocks:
        produit_nom = stock.produit.nom if stock.produit else "N/A"
        entrepot_nom = stock.entrepot.nom if stock.entrepot else "N/A"
        print(f"  - {produit_nom}")
        print(f"    Entrepôt: {entrepot_nom}")
        print(f"    Quantité: {stock.quantite}")
        print()

if __name__ == "__main__":
    check_data()




