#!/usr/bin/env python3
"""
Script de test complet pour toutes les APIs
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

class APITester:
    def __init__(self):
        self.results = []
        self.auth_token = None
        self.user_id = None
        self.entreprise_id = None
        self.boutique_id = None
        self.produit_id = None
        self.facture_id = None
    
    def log_test(self, test_name, success, message, data=None):
        """Enregistrer le résultat d'un test"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Données: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def test_connection(self):
        """Test de connexion au serveur"""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            self.log_test("Connexion serveur", True, f"Statut: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError:
            self.log_test("Connexion serveur", False, "Serveur non accessible")
            return False
        except Exception as e:
            self.log_test("Connexion serveur", False, f"Erreur: {e}")
            return False
    
    def test_inscription(self):
        """Test de l'inscription d'entreprise"""
        test_data = {
            "user": {
                "nom": "Test",
                "prenom": "API",
                "email": f"test.api.{int(time.time())}@example.com",
                "telephone": "+237 6XX XX XX XX",
                "mot_de_passe": "testpassword123",
                "role": "superadmin"
            },
            "nom": f"Entreprise Test {int(time.time())}",
            "description": "Entreprise créée par test API",
            "secteur_activite": "Technologie et Informatique",
            "adresse": "123 Rue Test",
            "ville": "Douala",
            "code_postal": "00000",
            "pays": "Cameroun",
            "telephone": "+237 2XX XX XX XX",
            "email": f"contact.test.{int(time.time())}@example.com",
            "site_web": "https://www.test-example.com",
            "numero_fiscal": "123456789",
            "nombre_employes": 5,
            "annee_creation": 2020,
            "pack_type": "professionnel",
            "pack_prix": 49,
            "pack_duree": "mensuel",
            "is_active": True
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/inscription/inscription/",
                json=test_data,
                headers=HEADERS
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    self.entreprise_id = data['entreprise']['id_entreprise']
                    self.log_test("Inscription entreprise", True, "Entreprise créée avec succès")
                    return True
                else:
                    self.log_test("Inscription entreprise", False, data.get('message', 'Erreur inconnue'))
            else:
                self.log_test("Inscription entreprise", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Inscription entreprise", False, f"Erreur: {e}")
        
        return False
    
    def test_login(self):
        """Test de connexion utilisateur"""
        login_data = {
            "username": f"test.api.{int(time.time())}@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=login_data,
                headers=HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.user_id = data.get('user_id')
                self.log_test("Connexion utilisateur", True, "Connexion réussie")
                return True
            else:
                self.log_test("Connexion utilisateur", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Connexion utilisateur", False, f"Erreur: {e}")
        
        return False
    
    def test_entreprises_list(self):
        """Test de récupération des entreprises"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/entreprises/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Liste entreprises", True, f"{len(data)} entreprises trouvées")
                return True
            else:
                self.log_test("Liste entreprises", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste entreprises", False, f"Erreur: {e}")
        
        return False
    
    def test_boutiques_list(self):
        """Test de récupération des boutiques"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/boutiques/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    self.boutique_id = data[0]['id']
                self.log_test("Liste boutiques", True, f"{len(data)} boutiques trouvées")
                return True
            else:
                self.log_test("Liste boutiques", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste boutiques", False, f"Erreur: {e}")
        
        return False
    
    def test_produits_list(self):
        """Test de récupération des produits"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/produits/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Liste produits", True, f"{len(data)} produits trouvés")
                return True
            else:
                self.log_test("Liste produits", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste produits", False, f"Erreur: {e}")
        
        return False
    
    def test_create_produit(self):
        """Test de création d'un produit"""
        if not self.boutique_id:
            self.log_test("Création produit", False, "Pas de boutique disponible")
            return False
        
        produit_data = {
            "nom": f"Produit Test {int(time.time())}",
            "description": "Produit créé par test API",
            "categorie": "informatique",
            "prix_achat": 100.0,
            "prix_vente": 150.0,
            "stock_actuel": 10,
            "stock_minimum": 5,
            "boutique": self.boutique_id,
            "marque": "Test Brand",
            "modele": "Test Model",
            "processeur": "Intel i5",
            "ram": "8GB",
            "stockage": "256GB SSD",
            "systeme_exploitation": "Windows 10",
            "annee": 2023
        }
        
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.post(
                f"{BASE_URL}/produits/",
                json=produit_data,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                self.produit_id = data['id']
                self.log_test("Création produit", True, f"Produit créé avec ID: {self.produit_id}")
                return True
            else:
                self.log_test("Création produit", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Création produit", False, f"Erreur: {e}")
        
        return False
    
    def test_factures_list(self):
        """Test de récupération des factures"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/factures/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Liste factures", True, f"{len(data)} factures trouvées")
                return True
            else:
                self.log_test("Liste factures", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste factures", False, f"Erreur: {e}")
        
        return False
    
    def test_journaux_list(self):
        """Test de récupération des journaux"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/journaux/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Liste journaux", True, f"{len(data)} entrées de journal trouvées")
                return True
            else:
                self.log_test("Liste journaux", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste journaux", False, f"Erreur: {e}")
        
        return False
    
    def test_users_list(self):
        """Test de récupération des utilisateurs"""
        headers = HEADERS.copy()
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        
        try:
            response = requests.get(f"{BASE_URL}/users/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Liste utilisateurs", True, f"{len(data)} utilisateurs trouvés")
                return True
            else:
                self.log_test("Liste utilisateurs", False, f"Statut: {response.status_code}, Réponse: {response.text}")
                
        except Exception as e:
            self.log_test("Liste utilisateurs", False, f"Erreur: {e}")
        
        return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Tests API - StoRage Management System")
        print("=" * 60)
        
        # Tests de base
        if not self.test_connection():
            print("\n❌ Impossible de se connecter au serveur. Arrêt des tests.")
            return
        
        # Test d'inscription
        self.test_inscription()
        
        # Tests nécessitant une authentification
        if self.auth_token:
            self.test_entreprises_list()
            self.test_boutiques_list()
            self.test_produits_list()
            self.test_create_produit()
            self.test_factures_list()
            self.test_journaux_list()
            self.test_users_list()
        else:
            print("\n⚠️  Pas de token d'authentification, tests limités")
        
        # Résumé
        self.print_summary()
    
    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total des tests: {total_tests}")
        print(f"✅ Réussis: {successful_tests}")
        print(f"❌ Échoués: {failed_tests}")
        print(f"📈 Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTS ÉCHOUÉS:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Sauvegarder les résultats
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Résultats sauvegardés dans: test_results.json")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
