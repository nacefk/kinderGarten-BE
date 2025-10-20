from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Tenant

ROLES = (
    ("admin", "Admin"),
    ("parent", "Parent"),
)

class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users")
    role = models.CharField(max_length=20, choices=ROLES, default="parent")



    def __str__(self):
        return f"{self.username} ({self.tenant.slug})"
