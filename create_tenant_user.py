#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the kinderGartenAPI directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "kinderGartenAPI"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinderGartenAPI.settings")
django.setup()

from core.models import Tenant
from accounts.models import User

# Get or create the tenant
tenant = Tenant.objects.get(slug="new-kindergarten")

# Create a user for this tenant
user, created = User.objects.get_or_create(
    username="tenant-user",
    defaults={
        "email": "user@new-kindergarten.local",
        "first_name": "Tenant",
        "last_name": "User",
        "is_staff": False,
        "is_superuser": False,
        "tenant": tenant,
        "role": "director",
    },
)

if created:
    password = "tenant123"
    user.set_password(password)
    user.save()
    print(f"✓ Created user for '{tenant.name}' tenant")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Password: {password}")
    print(f"  Role: {user.role}")
else:
    print(f"✓ User already exists: {user.username}")

print(f"\n✓ User is linked to tenant: {user.tenant.name}")
