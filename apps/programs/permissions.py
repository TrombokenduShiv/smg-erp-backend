from rest_framework import permissions

class IsProgramViewerOrAdmin(permissions.BasePermission):
    """
    Allows access if:
    1. User is Super Admin
    2. User created the program
    3. User is in the 'assigned_viewers' list
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'SUP':
            return True
        if obj.created_by == user:
            return True
        if obj.assigned_viewers.filter(id=user.id).exists():
            return True
        return False

class IsApplicant(permissions.BasePermission):
    """
    Allows access if the user is the one who applied.
    """
    def has_object_permission(self, request, view, obj):
        return obj.applicant == request.user