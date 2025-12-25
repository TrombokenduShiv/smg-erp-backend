from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    RBAC: Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUP'

class IsDeptAdmin(permissions.BasePermission):
    """
    RBAC: Allows access to Department Admins (and Super Admins).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADM', 'SUP']

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    ABAC (Attribute-Based): 
    - Admins can see everyone's data.
    - Interns can ONLY see their OWN data (obj.user == request.user).
    """
    def has_object_permission(self, request, view, obj):
        # Admin Override
        if request.user.role in ['SUP', 'ADM']:
            return True
        # Attribute Check
        return obj.user == request.user