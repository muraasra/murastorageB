#!/usr/bin/env python3
"""
Script de test final complet de toutes les APIs
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

def test_complete_api_suite():
    """Test complet de toutes les APIs"""
    print("🚀 TEST COMPLET DES APIs - StoRage Management System")
    print("=" * 70)
    
    results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    def log_test(test_name, success, message, data=None):
        results['total_tests'] += 1
        if success:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"
        
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'data': data
        }
        results['details'].append(result)
        
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Détails: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # 1. Test de connexion serveur
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        log_test("Connexion serveur", True, f"Statut: {response.status_code}")
    except Exception as e:
        log_test("Connexion serveur", False, f"Erreur: {e}")
        return results
    
    # 2. Création d'entreprise
    timestamp = int(time.time())
    inscription_data = {
        "user": {
            "nom": "Test",
            "prenom": "Final",
            "email": f"test.final.{timestamp}@example.com",
            "telephone": "+237 6XX XX XX XX",
            "mot_de_passe": "testpassword123",
            "role": "superadmin"
        },
        "nom": f"Entreprise Final {timestamp}",
        "description": "Entreprise créée pour test final",
        "secteur_activite": "Technologie et Informatique",
        "adresse": "123 Rue Final",
        "ville": "Douala",
        "code_postal": "00000",
        "pays": "Cameroun",
        "telephone": "+237 2XX XX XX XX",
        "email": f"contact.final.{timestamp}@example.com",
        "site_web": "https://www.final-example.com",
        "numero_fiscal": "123456789",
        "nombre_employes": 5,
        "annee_creation": 2020,
        "pack_type": "professionnel",
        "pack_prix": 49,
        "pack_duree": "mensuel",
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/inscription/inscription/", json=inscription_data, headers=HEADERS)
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                log_test("Création entreprise", True, f"Entreprise créée: {data['entreprise']['nom']}")
                email = inscription_data['user']['email']
            else:
                log_test("Création entreprise", False, data.get('message', 'Erreur inconnue'))
                return results
        else:
            log_test("Création entreprise", False, f"Statut: {response.status_code}")
            return results
    except Exception as e:
        log_test("Création entreprise", False, f"Erreur: {e}")
        return results
    
    # 3. Connexion utilisateur
    login_data = {"username": email, "password": "testpassword123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data['token']
            log_test("Connexion utilisateur", True, f"Token obtenu: {token[:20]}...")
        else:
            log_test("Connexion utilisateur", False, f"Statut: {response.status_code}")
            return results
    except Exception as e:
        log_test("Connexion utilisateur", False, f"Erreur: {e}")
        return results
    
    # Headers avec authentification
    auth_headers = HEADERS.copy()
    auth_headers['Authorization'] = f'Token {token}'
    
    # 4. Tests des APIs authentifiées
    api_tests = [
        ("/entreprises/", "Liste entreprises", "GET"),
        ("/boutiques/", "Liste boutiques", "GET"),
        ("/produits/", "Liste produits", "GET"),
        ("/factures/", "Liste factures", "GET"),
        ("/journaux/", "Liste journaux", "GET"),
        ("/users/", "Liste utilisateurs", "GET"),
    ]
    
    for endpoint, name, method in api_tests:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=auth_headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                log_test(name, True, f"{len(data)} éléments trouvés")
            else:
                log_test(name, False, f"Statut: {response.status_code}")
        except Exception as e:
            log_test(name, False, f"Erreur: {e}")
    
    # 5. Test création produit
    try:
        # Récupérer une boutique
        boutiques_response = requests.get(f"{BASE_URL}/boutiques/", headers=auth_headers)
        if boutiques_response.status_code == 200:
            boutiques = boutiques_response.json()
            if boutiques:
                boutique_id = boutiques[0]['id']
                
                produit_data = {
                    "nom": f"Produit Final {timestamp}",
                    "description": "Produit créé pour test final",
                    "category": "ordinateur",
                    "prix_achat": 100.0,
                    "prix": 150.0,
                    "quantite": 10,
                    "boutique": boutique_id,
                    "marque": "Final Brand",
                    "modele": "Final Model",
                    "processeur": "Intel i5",
                    "ram": "8GB",
                    "stockage": "256GB SSD",
                    "systeme_exploitation": "Windows 10",
                    "annee": 2023
                }
                
                response = requests.post(f"{BASE_URL}/produits/", json=produit_data, headers=auth_headers)
                if response.status_code == 201:
                    data = response.json()
                    log_test("Création produit", True, f"Produit créé: {data['nom']} (ID: {data['id']})")
                else:
                    log_test("Création produit", False, f"Statut: {response.status_code}")
            else:
                log_test("Création produit", False, "Aucune boutique disponible")
        else:
            log_test("Création produit", False, "Impossible de récupérer les boutiques")
    except Exception as e:
        log_test("Création produit", False, f"Erreur: {e}")
    
    # 6. Test vérification email
    try:
        verify_data = {
            "email": email,
            "verification_code": "123456"
        }
        response = requests.post(f"{BASE_URL}/email-verification/verify_code/", json=verify_data, headers=HEADERS)
        if response.status_code == 400:  # Code incorrect, mais endpoint fonctionne
            log_test("Vérification email", True, "Endpoint fonctionnel (code incorrect attendu)")
        else:
            log_test("Vérification email", False, f"Statut inattendu: {response.status_code}")
    except Exception as e:
        log_test("Vérification email", False, f"Erreur: {e}")
    
    return results

def print_final_summary(results):
    """Afficher le résumé final"""
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print("=" * 70)
    
    total = results['total_tests']
    passed = results['passed']
    failed = results['failed']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total des tests: {total}")
    print(f"✅ Réussis: {passed}")
    print(f"❌ Échoués: {failed}")
    print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    if failed > 0:
        print(f"\n❌ TESTS ÉCHOUÉS:")
        for detail in results['details']:
            if not detail['success']:
                print(f"  - {detail['test']}: {detail['message']}")
    
    # Sauvegarder les résultats
    with open('test_final_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Résultats sauvegardés dans: test_final_results.json")
    
    if success_rate >= 90:
        print(f"\n🎉 EXCELLENT! Le système fonctionne parfaitement!")
    elif success_rate >= 70:
        print(f"\n👍 BIEN! Le système fonctionne correctement avec quelques améliorations possibles.")
    else:
        print(f"\n⚠️  ATTENTION! Des problèmes nécessitent une attention.")

if __name__ == "__main__":
    results = test_complete_api_suite()
    print_final_summary(results)
