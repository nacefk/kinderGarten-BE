from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from core.models import Tenant
from .models import User


class TenantAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    tenant = serializers.CharField(write_only=True)

    def validate(self, attrs):
        tenant_slug = attrs.get("tenant")
        username = attrs.get("username")
        password = attrs.get("password")

        # 🔎 Find tenant by slug
        try:
            tenant = Tenant.objects.get(slug=tenant_slug)
        except Tenant.DoesNotExist:
            raise serializers.ValidationError({"tenant": "Invalid tenant slug"})

        # 🔐 Authenticate user (Django handles password)
        user = authenticate(username=username, password=password)
        if not user or user.tenant != tenant:
            raise serializers.ValidationError("Invalid credentials or tenant mismatch")

        # ✅ Generate JWT
        data = super().validate(attrs)
        data["tenant"] = tenant.slug
        data["tenant_name"] = tenant.name  # ✅ Add tenant name
        data["role"] = user.role
        data["username"] = user.username
        data["user_id"] = user.id
        data["email"] = user.email

        # ✅ If parent user, include their child's credentials (username, password, tenant)
        if user.role == "parent":
            try:
                child = user.children.first()  # Get the associated child
                if child:
                    data["credentials"] = {
                        "username": user.username,  # Parent username
                        "password": child.parent_password,  # Parent password
                        "tenant": tenant.slug,  # Tenant slug
                        "tenant_name": tenant.name,  # Tenant name
                        "child_name": child.name,  # Child name for reference
                    }
            except Exception:
                pass

        return data
