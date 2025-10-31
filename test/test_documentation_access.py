#!/usr/bin/env python3
"""
Test d'accès à la documentation Swagger/ReDoc
- Vérifier que la documentation est accessible
- Tester les différents formats
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_documentation_endpoints():
    """Test des endpoints de documentation."""
    print("📚 TEST DOCUMENTATION SWAGGER/REDOC")
    print("=" * 40)
    
    endpoints = [
        ("/swagger/", "Swagger UI"),
        ("/redoc/", "ReDoc UI"),
        ("/swagger.json", "Swagger JSON"),
        ("/swagger.yaml", "Swagger YAML"),
        ("/redoc/?format=openapi", "ReDoc OpenAPI"),
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = response.status_code
            print(f"   {name}: {status}")
            results[endpoint] = status
            
            if status == 200:
                print(f"      ✅ {name} accessible")
                
                # Vérifier le contenu pour les formats JSON/YAML
                if 'json' in endpoint or 'openapi' in endpoint:
                    try:
                        if endpoint.endswith('.json') or 'openapi' in endpoint:
                            data = response.json()
                            print(f"         📄 Contenu JSON valide")
                            print(f"         📋 Titre: {data.get('info', {}).get('title', 'N/A')}")
                            print(f"         📋 Version: {data.get('info', {}).get('version', 'N/A')}")
                            print(f"         📋 Endpoints: {len(data.get('paths', {}))}")
                    except:
                        print(f"         ❌ Contenu JSON invalide")
                        
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

def test_api_endpoints_in_docs():
    """Test des endpoints API dans la documentation."""
    print(f"\n🔍 TEST ENDPOINTS API DANS LA DOCUMENTATION")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/swagger.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            
            print(f"📋 Endpoints documentés: {len(paths)}")
            
            # Lister les endpoints principaux
            main_endpoints = [
                '/api/entreprises/',
                '/api/users/',
                '/api/boutiques/',
                '/api/produits/',
                '/api/factures/',
                '/api/auth/jwt/login/',
            ]
            
            for endpoint in main_endpoints:
                if endpoint in paths:
                    methods = list(paths[endpoint].keys())
                    print(f"   ✅ {endpoint}: {', '.join(methods)}")
                else:
                    print(f"   ❌ {endpoint}: Non trouvé")
            
            return True
        else:
            print(f"❌ Impossible de récupérer la documentation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_swagger_ui_access():
    """Test d'accès à l'interface Swagger UI."""
    print(f"\n🖥️  TEST INTERFACE SWAGGER UI")
    print("=" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/swagger/", timeout=10)
        print(f"📥 Statut Swagger UI: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'swagger' in content.lower():
                print(f"✅ Interface Swagger UI accessible")
                print(f"   🌐 URL: {BASE_URL}/swagger/")
                return True
            else:
                print(f"❌ Contenu Swagger UI invalide")
                return False
        else:
            print(f"❌ Swagger UI non accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Swagger UI: {e}")
        return False

def test_redoc_ui_access():
    """Test d'accès à l'interface ReDoc UI."""
    print(f"\n🖥️  TEST INTERFACE REDOC UI")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/redoc/", timeout=10)
        print(f"📥 Statut ReDoc UI: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'redoc' in content.lower():
                print(f"✅ Interface ReDoc UI accessible")
                print(f"   🌐 URL: {BASE_URL}/redoc/")
                return True
            else:
                print(f"❌ Contenu ReDoc UI invalide")
                return False
        else:
            print(f"❌ ReDoc UI non accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur ReDoc UI: {e}")
        return False

def main():
    print("🚀 TEST DOCUMENTATION SWAGGER/REDOC")
    print("=" * 40)
    
    # 1. Test des endpoints de documentation
    doc_results = test_documentation_endpoints()
    
    # 2. Test des endpoints API dans la documentation
    api_docs_success = test_api_endpoints_in_docs()
    
    # 3. Test des interfaces UI
    swagger_ui_success = test_swagger_ui_access()
    redoc_ui_success = test_redoc_ui_access()
    
    # 4. Résumé
    print(f"\n📊 RÉSUMÉ DOCUMENTATION")
    print("=" * 30)
    
    success_count = sum(1 for status in doc_results.values() if status == 200)
    total_count = len(doc_results)
    
    print(f"   📚 Endpoints documentation: {success_count}/{total_count}")
    print(f"   🔍 Endpoints API documentés: {'✅' if api_docs_success else '❌'}")
    print(f"   🖥️  Swagger UI: {'✅' if swagger_ui_success else '❌'}")
    print(f"   🖥️  ReDoc UI: {'✅' if redoc_ui_success else '❌'}")
    
    if success_count == total_count and api_docs_success and swagger_ui_success and redoc_ui_success:
        print(f"\n🎉 DOCUMENTATION COMPLÈTEMENT FONCTIONNELLE!")
        print(f"   ✅ Tous les endpoints de documentation sont accessibles")
        print(f"   ✅ Les interfaces Swagger et ReDoc fonctionnent")
        print(f"   ✅ Les endpoints API sont documentés")
        print(f"\n🌐 URLs d'accès:")
        print(f"   📖 Swagger UI: {BASE_URL}/swagger/")
        print(f"   📖 ReDoc UI: {BASE_URL}/redoc/")
        print(f"   📄 Swagger JSON: {BASE_URL}/swagger.json")
        print(f"   📄 Swagger YAML: {BASE_URL}/swagger.yaml")
    else:
        print(f"\n⚠️  Des problèmes persistent")
        if success_count < total_count:
            print(f"   - Vérifier les endpoints de documentation")
        if not api_docs_success:
            print(f"   - Vérifier la documentation des endpoints API")
        if not swagger_ui_success:
            print(f"   - Vérifier l'interface Swagger UI")
        if not redoc_ui_success:
            print(f"   - Vérifier l'interface ReDoc UI")

if __name__ == "__main__":
    main()























































