#!/usr/bin/env python3
"""
Test de charge pour simuler 100 utilisateurs avec 20 requêtes/minute chacun
Total: 2000 requêtes/minute = ~33 requêtes/seconde
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
import random

# Configuration du test
BASE_URL = "http://127.0.0.1:8000"
NUM_USERS = 100
REQUESTS_PER_USER_PER_MINUTE = 20
TEST_DURATION_MINUTES = 5  # Durée du test en minutes

# Endpoints à tester (pondérés par fréquence d'usage)
ENDPOINTS = [
    # Endpoints fréquents (80% des requêtes)
    {"path": "/api/produits/", "weight": 25, "method": "GET"},
    {"path": "/api/stocks/", "weight": 20, "method": "GET"},
    {"path": "/api/categories/", "weight": 15, "method": "GET"},
    {"path": "/api/fournisseurs/", "weight": 10, "method": "GET"},
    {"path": "/api/boutiques/", "weight": 10, "method": "GET"},
    
    # Endpoints moyens (15% des requêtes)
    {"path": "/api/factures/", "weight": 8, "method": "GET"},
    {"path": "/api/mouvements-stock/", "weight": 4, "method": "GET"},
    {"path": "/api/partenaires/", "weight": 3, "method": "GET"},
    
    # Endpoints rares (5% des requêtes)
    {"path": "/api/subscription-plans/", "weight": 2, "method": "GET"},
    {"path": "/api/subscriptions/current/", "weight": 2, "method": "GET"},
    {"path": "/api/subscriptions/usage/", "weight": 1, "method": "GET"},
]

class LoadTestResult:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.endpoints_stats: Dict[str, Dict[str, Any]] = {}
        
    def add_result(self, endpoint: str, method: str, status_code: int, 
                   response_time: float, error: str = None):
        result = {
            "timestamp": time.time(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "error": error
        }
        self.results.append(result)
        
        # Stats par endpoint
        if endpoint not in self.endpoints_stats:
            self.endpoints_stats[endpoint] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "response_times": [],
                "status_codes": {}
            }
        
        stats = self.endpoints_stats[endpoint]
        stats["total_requests"] += 1
        stats["response_times"].append(response_time)
        
        if status_code == 200:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
            
        stats["status_codes"][status_code] = stats["status_codes"].get(status_code, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
            
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r["status_code"] == 200)
        failed_requests = total_requests - successful_requests
        
        response_times = [r["response_time"] for r in self.results]
        
        duration = time.time() - self.start_time
        requests_per_second = total_requests / duration if duration > 0 else 0
        
        return {
            "test_duration_seconds": duration,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "requests_per_second": requests_per_second,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": self._percentile(response_times, 95) if response_times else 0,
            "p99_response_time": self._percentile(response_times, 99) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "endpoints_stats": self.endpoints_stats
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

async def simulate_user(session: aiohttp.ClientSession, user_id: int, 
                       result: LoadTestResult, auth_token: str = None):
    """Simule un utilisateur avec ses requêtes"""
    
    # Générer les requêtes pour cet utilisateur
    requests_per_second = REQUESTS_PER_USER_PER_MINUTE / 60
    interval = 1.0 / requests_per_second
    
    end_time = time.time() + (TEST_DURATION_MINUTES * 60)
    
    while time.time() < end_time:
        # Sélectionner un endpoint basé sur les poids
        endpoint = select_endpoint()
        
        start_time = time.time()
        try:
            headers = {"Content-Type": "application/json"}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            # Ajouter des paramètres de requête réalistes
            url = f"{BASE_URL}{endpoint['path']}"
            if "?" not in url and endpoint["path"] in ["/api/stocks/", "/api/factures/", "/api/mouvements-stock/"]:
                # Ajouter des filtres réalistes
                boutique_id = random.randint(1, 10)
                url += f"?entrepot={boutique_id}"
            
            async with session.request(
                endpoint["method"], 
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - start_time
                await response.text()  # Consommer la réponse
                
                result.add_result(
                    endpoint["path"], 
                    endpoint["method"], 
                    response.status,
                    response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            result.add_result(
                endpoint["path"], 
                endpoint["method"], 
                0,
                response_time,
                str(e)
            )
        
        # Attendre avant la prochaine requête
        await asyncio.sleep(interval)

def select_endpoint() -> Dict[str, Any]:
    """Sélectionne un endpoint basé sur les poids"""
    total_weight = sum(ep["weight"] for ep in ENDPOINTS)
    random_value = random.randint(1, total_weight)
    
    current_weight = 0
    for endpoint in ENDPOINTS:
        current_weight += endpoint["weight"]
        if random_value <= current_weight:
            return endpoint
    
    return ENDPOINTS[0]  # Fallback

async def get_auth_token(session: aiohttp.ClientSession) -> str:
    """Obtient un token d'authentification pour les tests"""
    try:
        login_data = {
            "username": "admin@example.com",  # Utilisateur de test
            "password": "admin123"
        }
        
        async with session.post(
            f"{BASE_URL}/api/auth/jwt/login/",
            json=login_data,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access_token")
    except Exception as e:
        print(f"Erreur lors de l'authentification: {e}")
    
    return None

async def run_load_test():
    """Lance le test de charge"""
    print(f"🚀 Démarrage du test de charge")
    print(f"   - Utilisateurs: {NUM_USERS}")
    print(f"   - Requêtes par utilisateur/minute: {REQUESTS_PER_USER_PER_MINUTE}")
    print(f"   - Durée: {TEST_DURATION_MINUTES} minutes")
    print(f"   - Total estimé: {NUM_USERS * REQUESTS_PER_USER_PER_MINUTE * TEST_DURATION_MINUTES} requêtes")
    print()
    
    result = LoadTestResult()
    
    # Configuration de la session HTTP
    connector = aiohttp.TCPConnector(
        limit=200,  # Limite de connexions totales
        limit_per_host=100,  # Limite par hôte
        ttl_dns_cache=300,  # Cache DNS
        use_dns_cache=True,
    )
    
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:
        
        # Obtenir un token d'authentification
        print("🔐 Authentification...")
        auth_token = await get_auth_token(session)
        if auth_token:
            print("✅ Authentification réussie")
        else:
            print("⚠️  Authentification échouée, tests sans auth")
        
        print(f"📊 Démarrage de {NUM_USERS} utilisateurs virtuels...")
        
        # Lancer tous les utilisateurs en parallèle
        tasks = [
            simulate_user(session, i, result, auth_token) 
            for i in range(NUM_USERS)
        ]
        
        await asyncio.gather(*tasks)
    
    return result

def print_results(result: LoadTestResult):
    """Affiche les résultats du test"""
    summary = result.get_summary()
    
    print("\n" + "="*60)
    print("📈 RÉSULTATS DU TEST DE CHARGE")
    print("="*60)
    
    print(f"⏱️  Durée du test: {summary['test_duration_seconds']:.2f} secondes")
    print(f"📊 Total requêtes: {summary['total_requests']}")
    print(f"✅ Requêtes réussies: {summary['successful_requests']}")
    print(f"❌ Requêtes échouées: {summary['failed_requests']}")
    print(f"📈 Taux de succès: {summary['success_rate']:.2f}%")
    print(f"🚀 Requêtes/seconde: {summary['requests_per_second']:.2f}")
    
    print(f"\n⏱️  TEMPS DE RÉPONSE:")
    print(f"   Moyenne: {summary['avg_response_time']:.3f}s")
    print(f"   Médiane: {summary['median_response_time']:.3f}s")
    print(f"   P95: {summary['p95_response_time']:.3f}s")
    print(f"   P99: {summary['p99_response_time']:.3f}s")
    print(f"   Min: {summary['min_response_time']:.3f}s")
    print(f"   Max: {summary['max_response_time']:.3f}s")
    
    print(f"\n📊 STATISTIQUES PAR ENDPOINT:")
    for endpoint, stats in summary['endpoints_stats'].items():
        success_rate = (stats['successful_requests'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
        avg_time = statistics.mean(stats['response_times']) if stats['response_times'] else 0
        
        print(f"   {endpoint}")
        print(f"     Requêtes: {stats['total_requests']} | Succès: {success_rate:.1f}% | Temps moyen: {avg_time:.3f}s")
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"load_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "summary": summary,
            "detailed_results": result.results
        }, f, indent=2)
    
    print(f"\n💾 Résultats sauvegardés dans: {filename}")

async def main():
    """Fonction principale"""
    try:
        result = await run_load_test()
        print_results(result)
        
        # Analyse des performances
        summary = result.get_summary()
        
        print(f"\n🔍 ANALYSE DES PERFORMANCES:")
        
        # Critères de performance
        if summary['success_rate'] >= 95:
            print("✅ Taux de succès: EXCELLENT")
        elif summary['success_rate'] >= 90:
            print("⚠️  Taux de succès: BON")
        else:
            print("❌ Taux de succès: INSUFFISANT")
        
        if summary['avg_response_time'] <= 0.5:
            print("✅ Temps de réponse moyen: EXCELLENT")
        elif summary['avg_response_time'] <= 1.0:
            print("⚠️  Temps de réponse moyen: BON")
        else:
            print("❌ Temps de réponse moyen: INSUFFISANT")
        
        if summary['p95_response_time'] <= 1.0:
            print("✅ P95 temps de réponse: EXCELLENT")
        elif summary['p95_response_time'] <= 2.0:
            print("⚠️  P95 temps de réponse: BON")
        else:
            print("❌ P95 temps de réponse: INSUFFISANT")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if summary['success_rate'] < 95:
            print("   - Optimiser la base de données (index, requêtes)")
            print("   - Augmenter les ressources serveur")
            print("   - Implémenter la mise en cache Redis")
        
        if summary['avg_response_time'] > 1.0:
            print("   - Optimiser les requêtes SQL")
            print("   - Implémenter la pagination")
            print("   - Utiliser la mise en cache côté serveur")
        
        if summary['p95_response_time'] > 2.0:
            print("   - Optimiser les endpoints les plus lents")
            print("   - Implémenter la compression gzip")
            print("   - Utiliser un CDN pour les assets statiques")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
