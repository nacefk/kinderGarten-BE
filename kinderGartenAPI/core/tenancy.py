from rest_framework.filters import BaseFilterBackend

class TenantFilterBackend(BaseFilterBackend):
    """
    Ensures every queryset is automatically filtered by request.user.tenant.
    Attach globally via DEFAULT_FILTER_BACKENDS or per-view.
    """
    def filter_queryset(self, request, queryset, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return queryset.none()
        # Only filter models that have a 'tenant' field
        if hasattr(queryset.model, "tenant_id"):
            return queryset.filter(tenant=user.tenant)
        return queryset
