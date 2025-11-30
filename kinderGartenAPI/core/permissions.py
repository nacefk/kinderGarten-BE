from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTenantAdmin(BasePermission):
    """Check if user is admin in their tenant"""

    message = "Only tenant admins can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.user.tenant


class IsTenantParent(BasePermission):
    """Check if user is parent in their tenant"""

    message = "Only parents can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "parent"
        )


class IsTenantMember(BasePermission):
    """Check if user belongs to same tenant as resource"""

    message = "You don't have access to this resource."

    def has_object_permission(self, request, view, obj):
        tenant_field = getattr(obj, "tenant", None)
        if tenant_field:
            return tenant_field == request.user.tenant
        return False
