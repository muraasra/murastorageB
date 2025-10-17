# core/management/commands/load_test.py
import time
import threading
from django.core.management.base import BaseCommand
from django.core.cache import cache
from core.models import Produit, Stock, Entreprise, Boutique, Facture
from django.db import connection
from django.db.models import Q

class Command(BaseCommand):
    help = 'Test de charge réaliste avec les optimisations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Nombre d\'utilisateurs virtuels (défaut: 50)'
        )
        parser.add_argument(
            '--requests',
            type=int,
            default=20,
            help='Nombre de requêtes par utilisateur (défaut: 20)'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Test de charge réaliste avec optimisations")
        
        # Créer des données de test
        self.create_test_data()
        
        # Test de charge
        self.run_load_test(options['users'], options['requests'])

    def create_test_data(self):
        """Créer des données de test si nécessaire"""
        try:
            # Vérifier si on a des données
            if not Entreprise.objects.exists():
                self.stdout.write("📝 Création de données de test...")
                
                # Créer une entreprise de test
                entreprise = Entreprise.objects.create(
                    nom="Entreprise Test Performance",
                    email="test@performance.com",
                    secteur_activite="Test",
                    adresse="Adresse test",
                    ville="Ville test",
                    pays="Cameroun",
                    annee_creation=2024
                )
                
                # Créer des boutiques de test
                for i in range(3):
                    Boutique.objects.create(
                        entreprise=entreprise,
                        nom=f"Boutique Test {i+1}",
                        ville="Ville test"
                    )
                
                # Créer des produits de test
                boutique = Boutique.objects.first()
                for i in range(50):
                    Produit.objects.create(
                        nom=f"Produit Test {i+1}",
                        entreprise=entreprise,
                        prix_achat=100 + i,
                        prix_vente=150 + i,
                        quantite=10 + i,
                        actif=True
                    )
                
                # Créer des stocks de test
                produits = Produit.objects.all()[:20]
                for produit in produits:
                    Stock.objects.create(
                        produit=produit,
                        entrepot=boutique,
                        quantite=produit.quantite
                    )
                
                self.stdout.write("✅ Données de test créées")
                
        except Exception as e:
            self.stdout.write(f"⚠️  Erreur création données test: {str(e)}")

    def simulate_user_requests(self, user_id, num_requests):
        """Simuler les requêtes d'un utilisateur"""
        total_time = 0
        successful_requests = 0
        errors = 0
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                
                # Simuler différentes requêtes selon le type
                request_type = i % 5
                
                if request_type == 0:
                    # Requête produits avec cache
                    cache_key = f"produits_user_{user_id}_{i}"
                    cached_data = cache.get(cache_key)
                    if cached_data is None:
                        produits = list(Produit.objects.filter(entreprise_id=1, actif=True)[:10])
                        cache.set(cache_key, produits, 300)
                    else:
                        produits = cached_data
                        
                elif request_type == 1:
                    # Requête stocks optimisée
                    stocks = list(Stock.objects.filter(entrepot_id=1).select_related('produit')[:10])
                    
                elif request_type == 2:
                    # Requête complexe avec jointures
                    produits = list(Produit.objects.filter(
                        entreprise_id=1, 
                        actif=True,
                        categorie__isnull=False
                    ).select_related('categorie', 'entreprise')[:5])
                    
                elif request_type == 3:
                    # Requête avec filtrage et tri
                    produits = list(Produit.objects.filter(
                        entreprise_id=1,
                        prix_vente__gte=100
                    ).order_by('-prix_vente')[:10])
                    
                else:
                    # Requête avec cache et invalidation
                    cache_key = f"test_user_{user_id}_{i}"
                    cache.set(cache_key, {"data": f"test_{i}", "timestamp": time.time()}, 60)
                    cached_data = cache.get(cache_key)
                    cache.delete(cache_key)
                
                end_time = time.time()
                total_time += (end_time - start_time)
                successful_requests += 1
                
                # Petite pause pour simuler un comportement réaliste
                time.sleep(0.01)
                
            except Exception as e:
                errors += 1
                if errors <= 3:  # Limiter les messages d'erreur
                    self.stdout.write(f"  ⚠️  Erreur utilisateur {user_id}, requête {i}: {str(e)}")
        
        return total_time, successful_requests, errors

    def run_load_test(self, num_users, requests_per_user):
        """Exécuter le test de charge"""
        self.stdout.write(f"\n🔥 Test de charge: {num_users} utilisateurs, {requests_per_user} requêtes chacun")
        self.stdout.write(f"📊 Total estimé: {num_users * requests_per_user} requêtes")
        
        start_time = time.time()
        
        # Créer les threads pour simuler les utilisateurs
        threads = []
        results = []
        
        def worker(user_id):
            result = self.simulate_user_requests(user_id, requests_per_user)
            results.append(result)
        
        # Lancer les threads
        for i in range(num_users):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_test_time = end_time - start_time
        
        # Analyser les résultats
        total_requests = sum(r[1] for r in results)
        total_errors = sum(r[2] for r in results)
        total_time = sum(r[0] for r in results)
        
        avg_response_time = total_time / total_requests if total_requests > 0 else 0
        requests_per_second = total_requests / total_test_time if total_test_time > 0 else 0
        success_rate = (total_requests / (total_requests + total_errors)) * 100 if (total_requests + total_errors) > 0 else 0
        
        self.stdout.write(f"\n📈 RÉSULTATS DU TEST DE CHARGE")
        self.stdout.write(f"⏱️  Durée totale: {total_test_time:.2f}s")
        self.stdout.write(f"📊 Requêtes totales: {total_requests}")
        self.stdout.write(f"❌ Erreurs: {total_errors}")
        self.stdout.write(f"✅ Taux de succès: {success_rate:.1f}%")
        self.stdout.write(f"🚀 Requêtes/seconde: {requests_per_second:.2f}")
        self.stdout.write(f"⚡ Temps de réponse moyen: {avg_response_time:.4f}s")
        
        # Évaluer les performances
        self.stdout.write(f"\n🔍 ANALYSE:")
        if success_rate >= 95:
            self.stdout.write("✅ Taux de succès: EXCELLENT")
        elif success_rate >= 90:
            self.stdout.write("✅ Taux de succès: BON")
        elif success_rate >= 80:
            self.stdout.write("⚠️  Taux de succès: ACCEPTABLE")
        else:
            self.stdout.write("❌ Taux de succès: INSUFFISANT")
        
        if requests_per_second >= 100:
            self.stdout.write("✅ Débit: EXCELLENT")
        elif requests_per_second >= 50:
            self.stdout.write("✅ Débit: BON")
        elif requests_per_second >= 20:
            self.stdout.write("⚠️  Débit: ACCEPTABLE")
        else:
            self.stdout.write("❌ Débit: INSUFFISANT")
        
        if avg_response_time <= 0.1:
            self.stdout.write("✅ Temps de réponse: EXCELLENT")
        elif avg_response_time <= 0.2:
            self.stdout.write("✅ Temps de réponse: BON")
        elif avg_response_time <= 0.5:
            self.stdout.write("⚠️  Temps de réponse: ACCEPTABLE")
        else:
            self.stdout.write("❌ Temps de réponse: LENT")
        
        # Projection pour 100 utilisateurs
        projected_rps = requests_per_second * (100 / num_users)
        projected_requests_per_minute = projected_rps * 60
        
        self.stdout.write(f"\n📊 PROJECTION POUR 100 UTILISATEURS:")
        self.stdout.write(f"🚀 Requêtes/seconde estimées: {projected_rps:.1f}")
        self.stdout.write(f"📈 Requêtes/minute estimées: {projected_requests_per_minute:.0f}")
        
        if projected_rps >= 50:
            self.stdout.write("✅ Le système peut supporter 100 utilisateurs simultanés")
        elif projected_rps >= 30:
            self.stdout.write("⚠️  Le système peut supporter 100 utilisateurs avec optimisations")
        else:
            self.stdout.write("❌ Le système nécessite des optimisations supplémentaires")

