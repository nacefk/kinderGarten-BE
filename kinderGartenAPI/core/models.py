# core/models.py
from django.db import models

class Tenant(models.Model):
    """
    Each kindergarten or crèche is a separate tenant.
    All data (children, staff, reports, etc.) are scoped to this tenant.
    """
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)  # e.g. "arc-en-ciel"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BaseTenantModel(models.Model):
    """
    Abstract base class that adds a 'tenant' ForeignKey to any model
    that belongs to a specific kindergarten.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ["id"]  # Optional, keeps things consistent in admin

    def __str__(self):
        # For debug clarity — show tenant context in derived models
        tenant_name = getattr(self.tenant, "slug", "?")
        return f"{self.__class__.__name__} (tenant={tenant_name})"
