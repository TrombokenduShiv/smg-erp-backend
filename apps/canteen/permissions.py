from rest_framework import permissions

class IsCanteenStaff(permissions.BasePermission):
    """
    Allows access only if the user belongs to the 'CANTEEN' department.
    """
    def has_permission(self, request, view):
        # Must be logged in
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check Department (Ensure your User model has this field populated correctly)
        return request.user.department == 'CANTEEN'