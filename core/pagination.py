# core/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.core.cache import cache
import hashlib
import json

class OptimizedPageNumberPagination(PageNumberPagination):
    """
    Pagination optimisée avec cache et métadonnées enrichies
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Retourne une réponse paginée avec métadonnées enrichies
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'pagination': {
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.page.paginator.per_page,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
            }
        })

class CachedPageNumberPagination(OptimizedPageNumberPagination):
    """
    Pagination avec cache pour les requêtes fréquentes
    """
    cache_timeout = 300  # 5 minutes
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Pagine le queryset avec cache
        """
        # Générer une clé de cache basée sur la requête
        cache_key = self._generate_cache_key(queryset, request)
        
        # Vérifier le cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            # Reconstituer la page depuis le cache
            self.page = cached_data['page']
            self.request = request
            return self.page.object_list
        
        # Paginer normalement
        page = super().paginate_queryset(queryset, request, view)
        
        # Mettre en cache
        if page is not None:
            cache_data = {
                'page': self.page,
                'count': self.page.paginator.count,
            }
            cache.set(cache_key, cache_data, self.cache_timeout)
        
        return page
    
    def _generate_cache_key(self, queryset, request):
        """
        Génère une clé de cache unique pour la requête
        """
        # Inclure les paramètres de pagination
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.page_size)
        
        # Inclure les paramètres de filtrage
        query_params = dict(request.GET)
        
        # Inclure l'utilisateur si authentifié
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        # Inclure l'entreprise si disponible
        entreprise_id = request.user.entreprise.id if (
            request.user.is_authenticated and 
            hasattr(request.user, 'entreprise') and 
            request.user.entreprise
        ) else None
        
        # Construire la clé
        key_parts = [
            'paginated',
            request.path,
            str(user_id),
            str(entreprise_id) if entreprise_id else 'no_entreprise',
            str(page),
            str(page_size),
            json.dumps(query_params, sort_keys=True)
        ]
        
        key_string = ':'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

class FastPagination(PageNumberPagination):
    """
    Pagination ultra-rapide pour les listes volumineuses
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        """
        Réponse simplifiée pour la performance
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

class SmartPagination(OptimizedPageNumberPagination):
    """
    Pagination intelligente qui s'adapte au contexte
    """
    
    def get_page_size(self, request):
        """
        Détermine la taille de page optimale selon le contexte
        """
        # Taille par défaut selon le type de données
        if 'produits' in request.path:
            default_size = 50
        elif 'stocks' in request.path:
            default_size = 100
        elif 'factures' in request.path:
            default_size = 30
        elif 'mouvements' in request.path:
            default_size = 100
        else:
            default_size = 50
        
        # Permettre la surcharge via paramètre
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size > 0 and page_size <= self.max_page_size:
                    return page_size
            except (ValueError, TypeError):
                pass
        
        return default_size

