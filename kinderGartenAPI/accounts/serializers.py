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
        data["role"] = user.role
        data["username"] = user.username
        return data
