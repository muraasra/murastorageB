# core/cache_utils.py
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from functools import wraps
import hashlib
import json
from typing import Any, Optional, Callable
from django.http import HttpRequest
from rest_framework.response import Response

def cache_api_response(timeout: int = 300, key_prefix: str = 'api', vary_on_user: bool = True):
    """
    Décorateur pour mettre en cache les réponses d'API
    
    Args:
        timeout: Durée du cache en secondes (défaut: 5 minutes)
        key_prefix: Préfixe pour la clé de cache
        vary_on_user: Si True, varie le cache selon l'utilisateur
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(self, request: HttpRequest, *args, **kwargs) -> Response:
            # Construire la clé de cache
            cache_key_parts = [key_prefix]
            
            # Ajouter l'utilisateur si nécessaire
            if vary_on_user and hasattr(request, 'user') and request.user.is_authenticated:
                cache_key_parts.append(f"user_{request.user.id}")
            
            # Ajouter les paramètres de requête
            query_params = dict(request.GET)
            if query_params:
                params_str = json.dumps(query_params, sort_keys=True)
                params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
                cache_key_parts.append(f"params_{params_hash}")
            
            # Ajouter l'entreprise si disponible
            if hasattr(request, 'user') and request.user.is_authenticated and request.user.entreprise:
                cache_key_parts.append(f"entreprise_{request.user.entreprise.id}")
            
            # Ajouter la boutique si disponible
            if hasattr(request, 'user') and request.user.is_authenticated and request.user.boutique:
                cache_key_parts.append(f"boutique_{request.user.boutique.id}")
            
            # Ajouter le chemin de la requête
            cache_key_parts.append(request.path.replace('/', '_'))
            
            cache_key = ':'.join(cache_key_parts)
            
            # Vérifier le cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)
            
            # Exécuter la vue
            response = view_func(self, request, *args, **kwargs)
            
            # Mettre en cache si c'est une réponse valide
            if response.status_code == 200 and hasattr(response, 'data'):
                cache.set(cache_key, response.data, timeout)
            
            return response
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """
    Invalide le cache selon un pattern
    
    Args:
        pattern: Pattern de clé à invalider (ex: 'api:produits:*')
    """
    try:
        from django.core.cache import cache
        
        # Pour LocMemCache, on ne peut pas utiliser delete_pattern
        # On doit vider tout le cache ou utiliser une approche différente
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # Pour cache local, on vide tout le cache
            # C'est une solution simple mais efficace pour le développement
            cache.clear()
    except Exception as e:
        print(f"Erreur lors de l'invalidation du cache: {e}")

def cache_model_instance(model_class, instance_id: int, timeout: int = 300):
    """
    Met en cache une instance de modèle
    
    Args:
        model_class: Classe du modèle
        instance_id: ID de l'instance
        timeout: Durée du cache en secondes
    """
    cache_key = f"model_{model_class.__name__.lower()}_{instance_id}"
    
    # Vérifier le cache
    cached_instance = cache.get(cache_key)
    if cached_instance is not None:
        return cached_instance
    
    # Récupérer depuis la base de données
    try:
        instance = model_class.objects.get(id=instance_id)
        cache.set(cache_key, instance, timeout)
        return instance
    except model_class.DoesNotExist:
        return None

def cache_queryset(queryset, cache_key: str, timeout: int = 300):
    """
    Met en cache un queryset
    
    Args:
        queryset: Queryset à mettre en cache
        cache_key: Clé de cache
        timeout: Durée du cache en secondes
    """
    # Vérifier le cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Exécuter le queryset et mettre en cache
    data = list(queryset.values())
    cache.set(cache_key, data, timeout)
    return data

class CacheManager:
    """Gestionnaire de cache pour les opérations fréquentes"""
    
    @staticmethod
    def get_user_entreprise_data(user_id: int, timeout: int = 600):
        """Cache les données d'entreprise d'un utilisateur"""
        cache_key = f"user_entreprise_{user_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            from .models import User
            try:
                user = User.objects.select_related('entreprise', 'boutique').get(id=user_id)
                cached_data = {
                    'entreprise_id': user.entreprise.id if user.entreprise else None,
                    'entreprise_nom': user.entreprise.nom if user.entreprise else None,
                    'boutique_id': user.boutique.id if user.boutique else None,
                    'boutique_nom': user.boutique.nom if user.boutique else None,
                }
                cache.set(cache_key, cached_data, timeout)
            except User.DoesNotExist:
                cached_data = None
        
        return cached_data
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalide le cache d'un utilisateur"""
        cache_key = f"user_entreprise_{user_id}"
        cache.delete(cache_key)
    
    @staticmethod
    def get_produits_by_entreprise(entreprise_id: int, timeout: int = 300):
        """Cache les produits d'une entreprise"""
        cache_key = f"produits_entreprise_{entreprise_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            from .models import Produit
            produits = Produit.objects.filter(entreprise_id=entreprise_id, actif=True)
            cached_data = list(produits.values(
                'id', 'nom', 'sku', 'prix_vente', 'prix_achat', 
                'quantite', 'categorie_id', 'marque', 'modele'
            ))
            cache.set(cache_key, cached_data, timeout)
        
        return cached_data
    
    @staticmethod
    def invalidate_produits_cache(entreprise_id: int):
        """Invalide le cache des produits d'une entreprise"""
        cache_key = f"produits_entreprise_{entreprise_id}"
        cache.delete(cache_key)
        # Invalider aussi les réponses list() décorées avec cache_api_response
        # Cela couvre les clés du type "produits:user_<id>:params_<hash>:entreprise_<id>:_api_produits_"
        invalidate_cache_pattern('produits')
    
    @staticmethod
    def get_stocks_by_entrepot(entrepot_id: int, timeout: int = 180):
        """Cache les stocks d'un entrepôt"""
        cache_key = f"stocks_entrepot_{entrepot_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            from .models import Stock
            stocks = Stock.objects.filter(entrepot_id=entrepot_id).select_related('produit')
            cached_data = list(stocks.values(
                'id', 'produit_id', 'quantite', 'quantite_reservee', 
                'emplacement', 'produit__nom', 'produit__sku'
            ))
            cache.set(cache_key, cached_data, timeout)
        
        return cached_data
    
    @staticmethod
    def invalidate_stocks_cache(entrepot_id: int):
        """Invalide le cache des stocks d'un entrepôt"""
        cache_key = f"stocks_entrepot_{entrepot_id}"
        cache.delete(cache_key)

    @staticmethod
    def invalidate_api_prefix(prefix: str):
        """Invalide les caches générés par cache_api_response pour un préfixe donné."""
        try:
            # Tenter avec wildcard (Redis) puis fallback simple
            invalidate_cache_pattern(f"{prefix}:*")
            invalidate_cache_pattern(prefix)
        except Exception as e:
            print(f"Erreur lors de l'invalidation du préfixe {prefix}: {e}")




















