# core/management/commands/performance_test.py
import asyncio
import time
import json
from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.models import Produit, Stock, Entreprise, Boutique, Facture
from django.db import connection
from django.db.models import Q

class Command(BaseCommand):
    help = 'Test de performance avec les optimisations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Nombre d\'utilisateurs virtuels (défaut: 20)'
        )
        parser.add_argument(
            '--requests',
            type=int,
            default=50,
            help='Nombre de requêtes par utilisateur (défaut: 50)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Test de performance avec optimisations")
        
        # Test 1: Performance des requêtes avec index
        self.test_database_performance()
        
        # Test 2: Performance du cache Redis
        self.test_cache_performance()
        
        # Test 3: Test de charge simulé
        self.test_load_performance(options['users'], options['requests'])

    def test_database_performance(self):
        """Test des performances de base de données avec les nouveaux index"""
        self.stdout.write("\n📊 Test des performances de base de données...")
        
        # Créer des données de test si nécessaire
        self.create_test_data()
        
        # Test des requêtes fréquentes
        queries_to_test = [
            {
                'name': 'Produits par entreprise',
                'query': lambda: Produit.objects.filter(entreprise_id=1, actif=True).count(),
                'expected_time': 0.1  # 100ms max
            },
            {
                'name': 'Stocks par entrepôt',
                'query': lambda: Stock.objects.filter(entrepot_id=1).select_related('produit').count(),
                'expected_time': 0.05  # 50ms max
            },
            {
                'name': 'Boutiques par entreprise',
                'query': lambda: Boutique.objects.filter(entreprise_id=1, is_active=True).count(),
                'expected_time': 0.05  # 50ms max
            },
            {
                'name': 'Requête complexe produits',
                'query': lambda: Produit.objects.filter(
                    entreprise_id=1, 
                    actif=True,
                    categorie__isnull=False
                ).select_related('categorie', 'entreprise').count(),
                'expected_time': 0.1  # 100ms max
            }
        ]
        
        for test in queries_to_test:
            try:
                start_time = time.time()
                result = test['query']()
                end_time = time.time()
                duration = end_time - start_time
                
                status = "✅" if duration <= test['expected_time'] else "❌"
                self.stdout.write(
                    f"  {status} {test['name']}: {duration:.3f}s "
                    f"(attendu: ≤{test['expected_time']}s) - Résultat: {result}"
                )
            except Exception as e:
                self.stdout.write(f"  ❌ {test['name']}: Erreur - {str(e)}")

    def test_cache_performance(self):
        """Test des performances du cache Redis"""
        self.stdout.write("\n💾 Test des performances du cache...")
        
        try:
            # Test de mise en cache
            cache_key = "test_performance"
            test_data = {"test": "data", "timestamp": time.time()}
            
            # Test écriture
            start_time = time.time()
            cache.set(cache_key, test_data, 300)
            write_time = time.time() - start_time
            
            # Test lecture
            start_time = time.time()
            cached_data = cache.get(cache_key)
            read_time = time.time() - start_time
            
            # Test invalidation
            start_time = time.time()
            cache.delete(cache_key)
            delete_time = time.time() - start_time
            
            self.stdout.write(f"  ✅ Écriture cache: {write_time:.4f}s")
            self.stdout.write(f"  ✅ Lecture cache: {read_time:.4f}s")
            self.stdout.write(f"  ✅ Suppression cache: {delete_time:.4f}s")
            
            # Vérifier que les données sont correctes
            if cached_data == test_data:
                self.stdout.write("  ✅ Intégrité des données: OK")
            else:
                self.stdout.write("  ❌ Intégrité des données: ÉCHEC")
                
        except Exception as e:
            self.stdout.write(f"  ❌ Erreur cache: {str(e)}")

    def test_load_performance(self, num_users, requests_per_user):
        """Test de charge simulé"""
        self.stdout.write(f"\n🔥 Test de charge: {num_users} utilisateurs, {requests_per_user} requêtes chacun")
        
        # Simuler des requêtes parallèles
        async def simulate_user_requests(user_id):
            """Simuler les requêtes d'un utilisateur"""
            total_time = 0
            successful_requests = 0
            
            for i in range(requests_per_user):
                try:
                    start_time = time.time()
                    
                    # Simuler différentes requêtes
                    if i % 4 == 0:
                        # Requête produits
                        list(Produit.objects.filter(entreprise_id=1, actif=True)[:10])
                    elif i % 4 == 1:
                        # Requête stocks
                        list(Stock.objects.filter(entrepot_id=1).select_related('produit')[:10])
                    elif i % 4 == 2:
                        # Requête avec cache
                        cache_key = f"test_user_{user_id}_request_{i}"
                        cache.set(cache_key, {"data": "test"}, 60)
                        cache.get(cache_key)
                    else:
                        # Requête complexe
                        list(Produit.objects.filter(
                            entreprise_id=1, 
                            actif=True,
                            categorie__isnull=False
                        ).select_related('categorie', 'entreprise')[:5])
                    
                    end_time = time.time()
                    total_time += (end_time - start_time)
                    successful_requests += 1
                    
                    # Petite pause pour simuler un comportement réaliste
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    self.stdout.write(f"  ⚠️  Erreur utilisateur {user_id}, requête {i}: {str(e)}")
            
            return total_time, successful_requests

        async def run_load_test():
            """Exécuter le test de charge"""
            start_time = time.time()
            
            # Créer les tâches pour tous les utilisateurs
            tasks = [simulate_user_requests(i) for i in range(num_users)]
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_test_time = end_time - start_time
            
            # Analyser les résultats
            total_requests = sum(r[1] for r in results)
            total_time = sum(r[0] for r in results)
            avg_response_time = total_time / total_requests if total_requests > 0 else 0
            requests_per_second = total_requests / total_test_time if total_test_time > 0 else 0
            
            self.stdout.write(f"  ⏱️  Durée totale: {total_test_time:.2f}s")
            self.stdout.write(f"  📊 Requêtes totales: {total_requests}")
            self.stdout.write(f"  🚀 Requêtes/seconde: {requests_per_second:.2f}")
            self.stdout.write(f"  ⚡ Temps de réponse moyen: {avg_response_time:.4f}s")
            
            # Évaluer les performances
            if requests_per_second >= 100:
                self.stdout.write("  ✅ Performance: EXCELLENTE")
            elif requests_per_second >= 50:
                self.stdout.write("  ✅ Performance: BONNE")
            elif requests_per_second >= 20:
                self.stdout.write("  ⚠️  Performance: ACCEPTABLE")
            else:
                self.stdout.write("  ❌ Performance: INSUFFISANTE")

        # Exécuter le test asynchrone
        try:
            asyncio.run(run_load_test())
        except Exception as e:
            self.stdout.write(f"  ❌ Erreur test de charge: {str(e)}")

    def create_test_data(self):
        """Créer des données de test si nécessaire"""
        try:
            # Vérifier si on a des données
            if not Entreprise.objects.exists():
                self.stdout.write("  📝 Création de données de test...")
                
                # Créer une entreprise de test
                entreprise = Entreprise.objects.create(
                    nom="Entreprise Test",
                    email="test@example.com",
                    secteur_activite="Test",
                    adresse="Adresse test",
                    ville="Ville test",
                    pays="Cameroun",
                    annee_creation=2024
                )
                
                # Créer une boutique de test
                boutique = Boutique.objects.create(
                    entreprise=entreprise,
                    nom="Boutique Test",
                    ville="Ville test"
                )
                
                self.stdout.write("  ✅ Données de test créées")
                
        except Exception as e:
            self.stdout.write(f"  ⚠️  Erreur création données test: {str(e)}")

    def test_query_optimization(self):
        """Test des optimisations de requêtes"""
        self.stdout.write("\n🔍 Test des optimisations de requêtes...")
        
        try:
            # Compter les requêtes SQL
            with connection.cursor() as cursor:
                # Test avec select_related
                start_time = time.time()
                produits = list(Produit.objects.filter(entreprise_id=1).select_related('categorie', 'entreprise')[:10])
                end_time = time.time()
                
                self.stdout.write(f"  ✅ Requête optimisée: {end_time - start_time:.4f}s")
                self.stdout.write(f"  📊 Nombre de produits: {len(produits)}")
                
                # Vérifier que les relations sont chargées
                if produits and hasattr(produits[0], 'categorie') and produits[0].categorie:
                    self.stdout.write("  ✅ Relations chargées: OK")
                else:
                    self.stdout.write("  ⚠️  Relations chargées: Partielles")
                    
        except Exception as e:
            self.stdout.write(f"  ❌ Erreur test requêtes: {str(e)}")




