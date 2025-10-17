#!/usr/bin/env python3
"""
Script de test pour vérifier les opérations CRUD des produits
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_crud_operations():
    """Teste les opérations CRUD pour les produits"""
    
    print("🧪 Test des opérations CRUD pour les produits")
    print("=" * 50)
    
    # Test 1: Lister les produits
    print("\n1. Test GET /produits/")
    try:
        response = requests.get(f"{BASE_URL}/produits/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {len(data)} produits trouvés")
            if data:
                print(f"   Premier produit: {data[0].get('nom', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Créer un produit
    print("\n2. Test POST /produits/")
    try:
        product_data = {
            "nom": "Test Produit",
            "description": "Produit de test pour vérifier les opérations CRUD",
            "prix_achat": 10000,
            "prix_vente": 15000,
            "stock_minimum": 5,
            "stock_maximum": 100,
            "unite_mesure": "piece",
            "etat_produit": "neuf",
            "marque": "Test Brand",
            "modele": "Test Model",
            "reference": "TEST-001",
            "category": "autre",
            "entreprise": 1,  # Assumant qu'il y a une entreprise avec ID 1
            "actif": True
        }
        
        response = requests.post(
            f"{BASE_URL}/produits/",
            json=product_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            created_product = response.json()
            product_id = created_product.get('id')
            print(f"   ✅ Succès: Produit créé avec ID {product_id}")
            print(f"   Nom: {created_product.get('nom')}")
            print(f"   SKU généré: {created_product.get('sku')}")
            return product_id
        else:
            print(f"   ❌ Erreur: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None
    
    # Test 3: Récupérer un produit spécifique
    print("\n3. Test GET /produits/{id}/")
    if product_id:
        try:
            response = requests.get(f"{BASE_URL}/produits/{product_id}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                product = response.json()
                print(f"   ✅ Succès: Produit récupéré")
                print(f"   Nom: {product.get('nom')}")
                print(f"   Prix: {product.get('prix_vente')} XAF")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 4: Modifier un produit
    print("\n4. Test PUT /produits/{id}/")
    if product_id:
        try:
            update_data = {
                "nom": "Test Produit Modifié",
                "description": "Description modifiée",
                "prix_achat": 12000,
                "prix_vente": 18000,
                "stock_minimum": 10,
                "stock_maximum": 150,
                "unite_mesure": "piece",
                "etat_produit": "neuf",
                "marque": "Test Brand Updated",
                "modele": "Test Model Updated",
                "reference": "TEST-001-UPDATED",
                "category": "autre",
                "entreprise": 1,
                "actif": True
            }
            
            response = requests.put(
                f"{BASE_URL}/produits/{product_id}/",
                json=update_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                updated_product = response.json()
                print(f"   ✅ Succès: Produit modifié")
                print(f"   Nouveau nom: {updated_product.get('nom')}")
                print(f"   Nouveau prix: {updated_product.get('prix_vente')} XAF")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 5: Supprimer un produit
    print("\n5. Test DELETE /produits/{id}/")
    if product_id:
        try:
            response = requests.delete(f"{BASE_URL}/produits/{product_id}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 204:
                print(f"   ✅ Succès: Produit supprimé")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 6: Test des fonctionnalités d'export
    print("\n6. Test GET /produits/export_produits/")
    try:
        response = requests.get(f"{BASE_URL}/produits/export_produits/?format=csv&entreprise=1")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Succès: Export CSV disponible")
            print(f"   Taille du fichier: {len(response.content)} bytes")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    test_crud_operations()
