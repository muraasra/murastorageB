from django.utils import timezone
from .models import Journal
from django.contrib.auth.models import User

class JournalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_response(self, request, response):
        # Ignorer les requêtes non authentifiées
        if not request.user.is_authenticated:
            return response

        # Ignorer les requêtes GET
        if request.method == 'GET':
            return response

        try:
            # Déterminer le type d'opération
            operation_type = self._get_operation_type(request)

            # Récupérer la boutique de l'utilisateur
            boutique = None
            if hasattr(request.user, 'boutique'):
                boutique = request.user.boutique
            elif hasattr(request.user, 'boutiques'):
                boutique = request.user.boutiques.first()

            # Créer l'entrée dans le journal
            Journal.objects.create(
                utilisateur=request.user,
                boutique=boutique,
                type_operation=operation_type,
                description=self._get_operation_description(request, operation_type),
                details=self._get_operation_details(request, response),
                date_operation=timezone.now(),
                ip_address=self._get_client_ip(request)
            )
        except Exception as e:
            print(f"Erreur lors de la journalisation: {str(e)}")

        return response

    def _get_operation_type(self, request):
        method = request.method.lower()
        if method == 'post':
            return 'creation'
        elif method == 'put' or method == 'patch':
            return 'modification'
        elif method == 'delete':
            return 'suppression'
        return 'autre'

    def _get_operation_description(self, request, operation_type):
        path = request.path.strip('/')
        parts = path.split('/')
        
        if len(parts) >= 2:
            resource = parts[-2]  # Prend le nom de la ressource avant l'ID
            if operation_type == 'creation':
                return f"Création d'un(e) {resource}"
            elif operation_type == 'modification':
                return f"Modification d'un(e) {resource}"
            elif operation_type == 'suppression':
                return f"Suppression d'un(e) {resource}"
        
        return f"Opération {operation_type}"

    def _get_operation_details(self, request, response):
        details = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
        }

        # Ajouter les données de la requête si elles existent
        if request.body:
            try:
                import json
                details['request_data'] = json.loads(request.body)
            except:
                pass

        return details

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 