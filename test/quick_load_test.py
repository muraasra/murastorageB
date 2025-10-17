#!/usr/bin/env python3
"""
Test de charge simplifié - Simulation rapide de 100 utilisateurs
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import random

# Configuration du test (réduite pour test rapide)
BASE_URL = "http://127.0.0.1:8000"
NUM_USERS = 20  # Réduit pour test rapide
REQUESTS_PER_USER = 10  # Réduit pour test rapide
TEST_DURATION_SECONDS = 30  # Test de 30 secondes

# Endpoints à tester
ENDPOINTS = [
    {"path": "/api/produits/", "weight": 30},
    {"path": "/api/stocks/", "weight": 25},
    {"path": "/api/categories/", "weight": 20},
    {"path": "/api/fournisseurs/", "weight": 15},
    {"path": "/api/boutiques/", "weight": 10},
]

class QuickLoadTest:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def add_result(self, endpoint, status_code, response_time, error=None):
        self.results.append({
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time,
            "error": error
        })
    
    def get_summary(self):
        if not self.results:
            return {}
            
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r["status_code"] == 200)
        failed_requests = total_requests - successful_requests
        
        response_times = [r["response_time"] for r in self.results]
        duration = time.time() - self.start_time
        requests_per_second = total_requests / duration if duration > 0 else 0
        
        return {
            "duration": duration,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "requests_per_second": requests_per_second,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": self._percentile(response_times, 95) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
        }
    
    def _percentile(self, data, percentile):
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

def select_endpoint():
    total_weight = sum(ep["weight"] for ep in ENDPOINTS)
    random_value = random.randint(1, total_weight)
    
    current_weight = 0
    for endpoint in ENDPOINTS:
        current_weight += endpoint["weight"]
        if random_value <= current_weight:
            return endpoint
    
    return ENDPOINTS[0]

async def simulate_user(session, user_id, result):
    """Simule un utilisateur avec ses requêtes"""
    end_time = time.time() + TEST_DURATION_SECONDS
    
    while time.time() < end_time:
        endpoint = select_endpoint()
        start_time = time.time()
        
        try:
            url = f"{BASE_URL}{endpoint['path']}"
            if "stocks" in endpoint["path"]:
                url += f"?entrepot={random.randint(1, 5)}"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = time.time() - start_time
                await response.text()
                
                result.add_result(
                    endpoint["path"], 
                    response.status,
                    response_time
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            result.add_result(
                endpoint["path"], 
                0,
                response_time,
                str(e)
            )
        
        # Attendre un peu entre les requêtes
        await asyncio.sleep(0.1)

async def run_quick_test():
    """Lance le test rapide"""
    print(f"🚀 Test de charge rapide")
    print(f"   - Utilisateurs: {NUM_USERS}")
    print(f"   - Durée: {TEST_DURATION_SECONDS} secondes")
    print(f"   - Total estimé: ~{NUM_USERS * REQUESTS_PER_USER} requêtes")
    print()
    
    result = QuickLoadTest()
    
    connector = aiohttp.TCPConnector(limit=50, limit_per_host=30)
    timeout = aiohttp.ClientTimeout(total=10, connect=5)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print(f"📊 Démarrage de {NUM_USERS} utilisateurs virtuels...")
        
        tasks = [simulate_user(session, i, result) for i in range(NUM_USERS)]
        await asyncio.gather(*tasks)
    
    return result

def print_results(result):
    """Affiche les résultats"""
    summary = result.get_summary()
    
    print("\n" + "="*50)
    print("📈 RÉSULTATS DU TEST DE CHARGE")
    print("="*50)
    
    print(f"⏱️  Durée: {summary['duration']:.2f}s")
    print(f"📊 Total requêtes: {summary['total_requests']}")
    print(f"✅ Requêtes réussies: {summary['successful_requests']}")
    print(f"❌ Requêtes échouées: {summary['failed_requests']}")
    print(f"📈 Taux de succès: {summary['success_rate']:.2f}%")
    print(f"🚀 Requêtes/seconde: {summary['requests_per_second']:.2f}")
    
    print(f"\n⏱️  TEMPS DE RÉPONSE:")
    print(f"   Moyenne: {summary['avg_response_time']:.3f}s")
    print(f"   Médiane: {summary['median_response_time']:.3f}s")
    print(f"   P95: {summary['p95_response_time']:.3f}s")
    print(f"   Max: {summary['max_response_time']:.3f}s")
    
    # Analyse des performances
    print(f"\n🔍 ANALYSE:")
    
    if summary['success_rate'] >= 95:
        print("✅ Taux de succès: EXCELLENT")
    elif summary['success_rate'] >= 90:
        print("⚠️  Taux de succès: BON")
    else:
        print("❌ Taux de succès: INSUFFISANT")
    
    if summary['avg_response_time'] <= 0.5:
        print("✅ Temps de réponse: EXCELLENT")
    elif summary['avg_response_time'] <= 1.0:
        print("⚠️  Temps de réponse: BON")
    else:
        print("❌ Temps de réponse: INSUFFISANT")
    
    # Projection pour 100 utilisateurs
    projected_rps = summary['requests_per_second'] * 5  # 5x plus d'utilisateurs
    projected_total = projected_rps * 60  # par minute
    
    print(f"\n📊 PROJECTION POUR 100 UTILISATEURS:")
    print(f"   Requêtes/seconde estimées: {projected_rps:.1f}")
    print(f"   Requêtes/minute estimées: {projected_total:.0f}")
    
    if projected_rps > 50:
        print("⚠️  Charge élevée détectée - Optimisations nécessaires")
    elif projected_rps > 20:
        print("✅ Charge modérée - Performance acceptable")
    else:
        print("✅ Charge faible - Performance excellente")

async def main():
    try:
        result = await run_quick_test()
        print_results(result)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())
