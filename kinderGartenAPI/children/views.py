from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
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
        return Club.objects.filter(tenant=self.request.user.tenant).order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class ClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        return Club.objects.filter(tenant=self.request.user.tenant).order_by("name")


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
            .order_by("name")  # ✅ Ordering for consistent pagination
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
                child.parent_password = password  # ✅ Save the password
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
# 👶 CHILD DETAIL - OPTIMIZED WITH MOBILE APP ACTIONS
# -----------------------------------------------------------
class ChildDetailView(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ OPTIMIZED queryset"""
        user = self.request.user
        qs = (
            Child.objects.filter(tenant=user.tenant)
            .select_related("classroom", "parent_user")  # ✅ FK optimization
            .prefetch_related("clubs")  # ✅ M2M optimization
            .order_by("name")  # ✅ Ordering for consistent pagination
        )

        if user.role == "parent":
            return qs.filter(parent_user=user)
        return qs

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsTenantMember],
    )
    def enable_mobile_app(self, request, pk=None):
        """Enable mobile app access for a child (create parent account if not exists)"""
        child = self.get_object()
        tenant = request.user.tenant

        # Check permission - only admins can enable/disable
        if request.user.role != "admin":
            raise PermissionDenied("Only admins can enable mobile app access")

        if child.has_mobile_app:
            return Response(
                {"message": "Mobile app is already enabled for this child"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # If no parent user exists, create one
                if not child.parent_user:
                    base_username = slugify(child.name)
                    username = base_username
                    if User.objects.filter(username=username).exists():
                        username = f"{base_username}_{get_random_string(3).lower()}"

                    password = get_random_string(
                        8,
                        allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789",
                    )

                    parent_user = User.objects.create_user(
                        username=username,
                        password=password,
                        tenant=tenant,
                        first_name=child.name,
                        role="parent",
                    )

                    child.parent_user = parent_user
                    child.parent_password = password
                else:
                    # Parent user exists, generate new password
                    password = get_random_string(
                        8,
                        allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789",
                    )
                    child.parent_password = password

                child.has_mobile_app = True
                child.save()

                logger.info(f"Enabled mobile app for child {child.id}")

                return Response(
                    {
                        "message": "Mobile app enabled successfully",
                        "credentials": {
                            "username": child.parent_user.username,
                            "password": child.parent_password,
                            "tenant": child.tenant.slug,
                            "tenant_name": child.tenant.name,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(
                f"Error enabling mobile app for child {pk}: {e}", exc_info=True
            )
            return Response(
                {"error": "Failed to enable mobile app"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsTenantMember],
    )
    def disable_mobile_app(self, request, pk=None):
        """Disable mobile app access and delete parent account"""
        child = self.get_object()

        # Check permission - only admins can enable/disable
        if request.user.role != "admin":
            raise PermissionDenied("Only admins can disable mobile app access")

        if not child.has_mobile_app:
            return Response(
                {"message": "Mobile app is not enabled for this child"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                parent_user = child.parent_user

                # Disable mobile app
                child.has_mobile_app = False
                child.parent_password = ""
                child.parent_user = None
                child.save()

                # Delete parent user account
                if parent_user:
                    username = parent_user.username
                    parent_user.delete()
                    logger.info(
                        f"Deleted parent account {username} for child {child.id}"
                    )

                logger.info(f"Disabled mobile app for child {child.id}")

                return Response(
                    {
                        "message": "Mobile app disabled and parent profile removed successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(
                f"Error disabling mobile app for child {pk}: {e}", exc_info=True
            )
            return Response(
                {"error": "Failed to disable mobile app"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
