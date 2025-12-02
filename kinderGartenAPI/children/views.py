from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
import logging

from children.models import Child, Club
from .models import ClassRoom
from children.serializers import (
    ChildSerializer,
    ChildListSerializer,
    ClassRoomSerializer,
)
from .serializers import ClubSerializer
from core.permissions import IsTenantAdmin, IsTenantParent, IsTenantMember

User = get_user_model()
logger = logging.getLogger("api")


# -----------------------------------------------------------
# 📚 CLASSROOM LIST / CREATE
# -----------------------------------------------------------
class ClassRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClassRoom.objects.filter(tenant=self.request.user.tenant).order_by(
            "name"
        )

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


# -----------------------------------------------------------
# 📚 CLASSROOM DETAIL / UPDATE / DELETE
# -----------------------------------------------------------
class ClassRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return ClassRoom.objects.filter(tenant=self.request.user.tenant)


# -----------------------------------------------------------
# 🎨 CLUBS
# -----------------------------------------------------------
class ClubListCreateView(generics.ListCreateAPIView):
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Club.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class ClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return Club.objects.filter(tenant=self.request.user.tenant)


# -----------------------------------------------------------
# 👶 CHILD LIST / CREATE - OPTIMIZED
# -----------------------------------------------------------
class ChildListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use lightweight serializer for list, full for create"""
        if self.request.method == "GET":
            return ChildListSerializer
        return ChildSerializer

    def get_queryset(self):
        """✅ OPTIMIZED: select_related + prefetch_related to prevent N+1"""
        user = self.request.user
        qs = (
            Child.objects.filter(tenant=user.tenant)
            .select_related("classroom", "parent_user")  # ✅ FK optimization
            .prefetch_related("clubs")  # ✅ M2M optimization
        )

        if user.role == "parent":
            qs = qs.filter(parent_user=user)

        classroom_id = self.request.query_params.get(
            "classroom_id"
        ) or self.request.query_params.get("classroom")
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)

        club_id = self.request.query_params.get(
            "club_id"
        ) or self.request.query_params.get("club")
        if club_id:
            qs = qs.filter(clubs__id=club_id).distinct()

        return qs

    @transaction.atomic  # ✅ Atomic transaction
    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        raw_flag = (
            self.request.data.get("has_mobile_app")
            or self.request.data.get("hasMobileApp")
            or False
        )
        has_mobile_app = str(raw_flag).lower() in ["true", "1", "yes"]

        try:
            child = serializer.save(tenant=tenant)
            logger.info(f"Created child {child.id} in tenant {tenant.slug}")

            if has_mobile_app:
                base_username = slugify(child.name)
                username = base_username
                if User.objects.filter(username=username).exists():
                    username = f"{base_username}_{get_random_string(3).lower()}"

                password = get_random_string(
                    8,
                    allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789",
                )

                user = User.objects.create_user(
                    username=username,
                    password=password,
                    tenant=tenant,
                    first_name=child.name,
                    role="parent",
                )

                child.parent_user = user
                child.save()

                self.generated_username = username
                self.generated_password = password
                logger.info(f"Created parent user {username} for child {child.id}")
            else:
                self.generated_username = None
                self.generated_password = None

        except Exception as e:
            logger.error(f"Error creating child: {e}", exc_info=True)
            raise

    def create(self, request, *args, **kwargs):
        """Return username/password if parent account was created"""
        response = super().create(request, *args, **kwargs)
        if getattr(self, "generated_username", None):
            response.data["username"] = self.generated_username
            response.data["password"] = self.generated_password
        return response


# -----------------------------------------------------------
# 👶 CHILD DETAIL - OPTIMIZED
# -----------------------------------------------------------
class ChildDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ OPTIMIZED queryset"""
        user = self.request.user
        qs = (
            Child.objects.filter(tenant=user.tenant)
            .select_related("classroom", "parent_user")  # ✅ FK optimization
            .prefetch_related("clubs")  # ✅ M2M optimization
        )

        if user.role == "parent":
            return qs.filter(parent_user=user)
        return qs


# -----------------------------------------------------------
# MY CHILD VIEW
# -----------------------------------------------------------
class MyChildView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantParent]

    def get_object(self):
        """✅ OPTIMIZED: Get parent's own child"""
        try:
            return (
                Child.objects.select_related("classroom", "parent_user")
                .prefetch_related("clubs")
                .get(parent_user=self.request.user)
            )
        except Child.DoesNotExist:
            logger.warning(f"Parent {self.request.user.id} has no child assigned")
            raise PermissionDenied("No child assigned to your account")
