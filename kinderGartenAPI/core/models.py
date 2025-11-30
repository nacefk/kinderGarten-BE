# core/models.py
from django.db import models


class Tenant(models.Model):
    """
    Each kindergarten or crèche is a separate tenant.
    All data (children, staff, reports, etc.) are scoped to this tenant.
    """

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class BaseTenantModel(models.Model):
    """
    Abstract base class that adds a 'tenant' ForeignKey to any model
    that belongs to a specific kindergarten. Enforces multi-tenant isolation.
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self):
        # For debug clarity — show tenant context in derived models
        tenant_name = getattr(self.tenant, "slug", "?")
        return f"{self.__class__.__name__} (tenant={tenant_name})"
