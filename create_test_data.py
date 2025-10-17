#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import Entreprise, Categorie, Fournisseur, Produit, User

def create_test_data():
    print("Création des données de test...")
    
    # Récupérer ou créer une entreprise de test
    try:
        entreprise = Entreprise.objects.first()
        if not entreprise:
            entreprise = Entreprise.objects.create(
                nom="Entreprise Test",
                description="Entreprise de test pour les produits",
                secteur_activite="Technologie",
                adresse="123 Rue Test",
                ville="Douala",
                pays="Cameroun",
                telephone="+237123456789",
                email="test@entreprise.com",
                annee_creation=2020,
                pack_type="professionnel"
            )
            print(f"[OK] Entreprise créée: {entreprise.nom}")
        else:
            print(f"[OK] Entreprise existante: {entreprise.nom}")
    except Exception as e:
        print(f"[ERROR] Erreur création entreprise: {e}")
        return
    
    # Créer des catégories
    categories_data = [
        {"nom": "Électronique", "description": "Produits électroniques"},
        {"nom": "Informatique", "description": "Produits informatiques", "parent_nom": "Électronique"},
        {"nom": "Téléphones", "description": "Téléphones et smartphones", "parent_nom": "Électronique"},
        {"nom": "Accessoires", "description": "Accessoires divers"},
    ]
    
    for cat_data in categories_data:
        try:
            parent = None
            if 'parent_nom' in cat_data:
                parent = Categorie.objects.filter(nom=cat_data['parent_nom'], entreprise=entreprise).first()
            
            categorie, created = Categorie.objects.get_or_create(
                nom=cat_data['nom'],
                entreprise=entreprise,
                defaults={
                    'description': cat_data['description'],
                    'parent': parent
                }
            )
            if created:
                print(f"[OK] Catégorie créée: {categorie.nom}")
            else:
                print(f"[OK] Catégorie existante: {categorie.nom}")
        except Exception as e:
            print(f"[ERROR] Erreur création catégorie {cat_data['nom']}: {e}")
    
    # Créer des fournisseurs
    fournisseurs_data = [
        {
            "nom": "TechSupply Cameroun",
            "code_fournisseur": "TSC001",
            "email": "contact@techsupply.cm",
            "telephone": "+237123456789",
            "adresse": "456 Avenue Tech",
            "ville": "Douala",
            "delai_livraison_jours": 3
        },
        {
            "nom": "ElectroDistrib",
            "code_fournisseur": "ED001",
            "email": "info@electrodistrib.cm",
            "telephone": "+237987654321",
            "adresse": "789 Boulevard Electro",
            "ville": "Yaoundé",
            "delai_livraison_jours": 5
        }
    ]
    
    for four_data in fournisseurs_data:
        try:
            fournisseur, created = Fournisseur.objects.get_or_create(
                code_fournisseur=four_data['code_fournisseur'],
                entreprise=entreprise,
                defaults=four_data
            )
            if created:
                print(f"[OK] Fournisseur créé: {fournisseur.nom}")
            else:
                print(f"[OK] Fournisseur existant: {fournisseur.nom}")
        except Exception as e:
            print(f"[ERROR] Erreur création fournisseur {four_data['nom']}: {e}")
    
    # Créer des produits de test
    produits_data = [
        {
            "nom": "iPhone 14 Pro",
            "description": "Smartphone Apple iPhone 14 Pro 128GB",
            "prix_achat": 800000,
            "prix_vente": 950000,
            "stock_minimum": 5,
            "stock_maximum": 50,
            "unite_mesure": "piece",
            "poids": 0.206,
            "couleur": "Or",
            "marque": "Apple",
            "modele": "iPhone 14 Pro",
            "categorie_nom": "Téléphones",
            "fournisseur_code": "TSC001"
        },
        {
            "nom": "MacBook Air M2",
            "description": "Ordinateur portable Apple MacBook Air avec puce M2",
            "prix_achat": 1200000,
            "prix_vente": 1400000,
            "stock_minimum": 3,
            "stock_maximum": 20,
            "unite_mesure": "piece",
            "poids": 1.24,
            "couleur": "Gris sidéral",
            "marque": "Apple",
            "modele": "MacBook Air M2",
            "categorie_nom": "Informatique",
            "fournisseur_code": "TSC001"
        },
        {
            "nom": "Samsung Galaxy S23",
            "description": "Smartphone Samsung Galaxy S23 256GB",
            "prix_achat": 750000,
            "prix_vente": 900000,
            "stock_minimum": 8,
            "stock_maximum": 40,
            "unite_mesure": "piece",
            "poids": 0.168,
            "couleur": "Noir",
            "marque": "Samsung",
            "modele": "Galaxy S23",
            "categorie_nom": "Téléphones",
            "fournisseur_code": "ED001"
        }
    ]
    
    for prod_data in produits_data:
        try:
            # Récupérer la catégorie
            categorie = Categorie.objects.filter(
                nom=prod_data['categorie_nom'], 
                entreprise=entreprise
            ).first()
            
            # Récupérer le fournisseur
            fournisseur = Fournisseur.objects.filter(
                code_fournisseur=prod_data['fournisseur_code'],
                entreprise=entreprise
            ).first()
            
            # Supprimer les clés qui ne sont pas des champs du modèle
            prod_data_clean = {k: v for k, v in prod_data.items() 
                             if k not in ['categorie_nom', 'fournisseur_code']}
            prod_data_clean['entreprise'] = entreprise
            prod_data_clean['categorie'] = categorie
            prod_data_clean['fournisseur_principal'] = fournisseur
            
            produit, created = Produit.objects.get_or_create(
                nom=prod_data['nom'],
                entreprise=entreprise,
                defaults=prod_data_clean
            )
            
            if created:
                print(f"[OK] Produit créé: {produit.nom} (SKU: {produit.sku})")
                print(f"   Code-barres: {produit.code_barres}")
                print(f"   QR Code: {produit.qr_code}")
            else:
                print(f"[OK] Produit existant: {produit.nom}")
        except Exception as e:
            print(f"[ERROR] Erreur création produit {prod_data['nom']}: {e}")
    
    print("\n[SUCCESS] Données de test créées avec succès!")
    print(f"[INFO] Résumé:")
    print(f"   - Entreprise: {Entreprise.objects.count()}")
    print(f"   - Catégories: {Categorie.objects.count()}")
    print(f"   - Fournisseurs: {Fournisseur.objects.count()}")
    print(f"   - Produits: {Produit.objects.count()}")

if __name__ == "__main__":
    create_test_data()
