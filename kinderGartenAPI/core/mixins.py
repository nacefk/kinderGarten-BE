class TenantSaveMixin:
    """Call serializer.save(tenant=request.user.tenant, ...) on create."""
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)
