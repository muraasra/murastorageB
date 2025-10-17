from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Autorise seulement les super admins à accéder.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'

class IsAdminOrSuperAdmin(BasePermission):
    """
    Autorise les admins de boutique et le superadmin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.role == 'superadmin'
        )

class IsSameBoutique(BasePermission):
    """
    Autorise uniquement les utilisateurs liés à la même boutique que l'objet consulté.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'superadmin':
            return True
        return hasattr(obj, 'boutique') and obj.boutique == request.user.boutique