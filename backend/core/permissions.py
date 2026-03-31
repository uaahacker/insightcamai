from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """Check if user is a member of the organization"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'organization'):
            return obj.organization.members.filter(user=request.user).exists()
        return False


class IsOrganizationAdmin(permissions.BasePermission):
    """Check if user is an admin of the organization"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'organization'):
            return obj.organization.members.filter(
                user=request.user,
                role__in=['admin', 'owner']
            ).exists()
        return False


class IsSuperAdmin(permissions.BasePermission):
    """Check if user is a superadmin"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit their own objects"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
