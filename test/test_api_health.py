#!/usr/bin/env python3
"""
Test de santé de l'API
- Vérifier que tous les endpoints fonctionnent
- Tester la documentation Swagger/ReDoc
- Identifier les problèmes éventuels
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_basic_endpoints():
    """Test des endpoints de base."""
    print("🔍 TEST ENDPOINTS DE BASE")
    print("=" * 30)
    
    endpoints = [
        ("/admin/", "Admin Django"),
        ("/api/", "API Root"),
        ("/swagger/", "Swagger UI"),
        ("/redoc/", "ReDoc"),
        ("/swagger.json", "Swagger JSON"),
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = response.status_code
            print(f"   {name}: {status}")
            results[endpoint] = status
            
            if status == 200:
                print(f"      ✅ {name} fonctionne")
            elif status == 404:
                print(f"      ⚠️  {name} non trouvé")
            elif status == 500:
                print(f"      ❌ {name} erreur serveur")
            else:
                print(f"      ⚠️  {name} statut inattendu: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Connexion impossible")
            results[endpoint] = "CONNECTION_ERROR"
        except requests.exceptions.Timeout:
            print(f"   {name}: ❌ Timeout")
            results[endpoint] = "TIMEOUT"
        except Exception as e:
            print(f"   {name}: ❌ Erreur: {e}")
            results[endpoint] = "ERROR"
    
    return results

def test_api_endpoints():
    """Test des endpoints API spécifiques."""
    print(f"\n🔍 TEST ENDPOINTS API")
    print("=" * 25)
    
    api_endpoints = [
        ("/api/entreprises/", "Entreprises"),
        ("/api/users/", "Utilisateurs"),
        ("/api/boutiques/", "Boutiques"),
        ("/api/produits/", "Produits"),
        ("/api/factures/", "Factures"),
        ("/api/auth/jwt/login/", "JWT Login"),
    ]
    
    results = {}
    
    for endpoint, name in api_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = response.status_code
            print(f"   {name}: {status}")
            results[endpoint] = status
            
            if status == 200:
                print(f"      ✅ {name} accessible")
            elif status == 401:
                print(f"      🔒 {name} nécessite authentification")
            elif status == 403:
                print(f"      🚫 {name} accès refusé")
            elif status == 404:
                print(f"      ⚠️  {name} non trouvé")
            elif status == 500:
                print(f"      ❌ {name} erreur serveur")
            else:
                print(f"      ⚠️  {name} statut: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Connexion impossible")
            results[endpoint] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"   {name}: ❌ Erreur: {e}")
            results[endpoint] = "ERROR"
    
    return results

def test_swagger_documentation():
    """Test spécifique de la documentation Swagger."""
    print(f"\n📚 TEST DOCUMENTATION SWAGGER")
    print("=" * 35)
    
    swagger_endpoints = [
        ("/swagger.json", "Swagger JSON Schema"),
        ("/swagger.yaml", "Swagger YAML Schema"),
        ("/redoc/?format=openapi", "ReDoc OpenAPI"),
    ]
    
    results = {}
    
    for endpoint, name in swagger_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = response.status_code
            print(f"   {name}: {status}")
            results[endpoint] = status
            
            if status == 200:
                print(f"      ✅ {name} accessible")
                # Vérifier le contenu
                if 'json' in endpoint:
                    try:
                        data = response.json()
                        print(f"         📄 Contenu JSON valide")
                    except:
                        print(f"         ❌ Contenu JSON invalide")
            elif status == 500:
                print(f"      ❌ {name} erreur serveur - Problème de configuration")
            else:
                print(f"      ⚠️  {name} statut: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Connexion impossible")
            results[endpoint] = "CONNECTION_ERROR"
        except Exception as e:
            print(f"   {name}: ❌ Erreur: {e}")
            results[endpoint] = "ERROR"
    
    return results

def test_server_health():
    """Test général de santé du serveur."""
    print(f"\n🏥 TEST SANTÉ SERVEUR")
    print("=" * 25)
    
    try:
        # Test de base
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Serveur Django fonctionne")
            return True
        else:
            print(f"   ⚠️  Serveur répond avec statut: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Serveur non accessible")
        return False
    except Exception as e:
        print(f"   ❌ Erreur serveur: {e}")
        return False

def main():
    print("🚀 TEST SANTÉ API COMPLET")
    print("=" * 35)
    
    # 1. Test de santé du serveur
    server_ok = test_server_health()
    if not server_ok:
        print("\n❌ Serveur non accessible - Arrêt des tests")
        return
    
    # 2. Tests des endpoints de base
    basic_results = test_basic_endpoints()
    
    # 3. Tests des endpoints API
    api_results = test_api_endpoints()
    
    # 4. Tests de la documentation
    swagger_results = test_swagger_documentation()
    
    # 5. Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 25)
    
    # Compter les succès
    total_tests = len(basic_results) + len(api_results) + len(swagger_results)
    success_count = 0
    
    for results in [basic_results, api_results, swagger_results]:
        for endpoint, status in results.items():
            if status == 200:
                success_count += 1
    
    print(f"   📈 Tests réussis: {success_count}/{total_tests}")
    
    # Identifier les problèmes
    problems = []
    for results in [basic_results, api_results, swagger_results]:
        for endpoint, status in results.items():
            if status == 500:
                problems.append(f"Erreur 500 sur {endpoint}")
            elif status == "CONNECTION_ERROR":
                problems.append(f"Connexion impossible sur {endpoint}")
    
    if problems:
        print(f"\n⚠️  PROBLÈMES IDENTIFIÉS:")
        for problem in problems:
            print(f"   - {problem}")
    else:
        print(f"\n🎉 AUCUN PROBLÈME MAJEUR DÉTECTÉ!")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    if any(status == 500 for results in [basic_results, api_results, swagger_results] for status in results.values()):
        print("   - Vérifier les logs Django pour les erreurs 500")
        print("   - Vérifier la configuration des serializers")
        print("   - Vérifier les migrations de base de données")
    
    if any(status == "CONNECTION_ERROR" for results in [basic_results, api_results, swagger_results] for status in results.values()):
        print("   - Vérifier que le serveur Django est démarré")
        print("   - Vérifier l'URL et le port (127.0.0.1:8000)")

if __name__ == "__main__":
    main()































