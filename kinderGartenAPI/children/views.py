from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from children.models import Child, Club
from .models import ClassRoom
from children.serializers import ChildSerializer, ClassRoomSerializer
from .serializers import ClubSerializer

User = get_user_model()


# -----------------------------------------------------------
# 📚 CLASSROOM LIST / CREATE
# -----------------------------------------------------------
class ClassRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClassRoom.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Club.objects.filter(tenant=self.request.user.tenant)


# -----------------------------------------------------------
# 👶 CHILD LIST / CREATE
# -----------------------------------------------------------
class ChildListCreateView(generics.ListCreateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Child.objects.filter(tenant=user.tenant)

        # ✅ Admins see all; parents only see their own child
        if user.role == "parent":
            return qs.filter(parent_user=user)

        # optional classroom/club filters (for admin)
        classroom_id = (
            self.request.query_params.get("classroom_id")
            or self.request.query_params.get("classroom")
        )
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)

        club_id = (
            self.request.query_params.get("club_id")
            or self.request.query_params.get("club")
        )
        if club_id:
            qs = qs.filter(clubs__id=club_id)

        return qs

    def perform_create(self, serializer):
        tenant = self.request.user.tenant

        # ✅ Extract has_mobile_app flag
        raw_flag = (
            self.request.data.get("has_mobile_app")
            or self.request.data.get("hasMobileApp")
            or False
        )
        has_mobile_app = str(raw_flag).lower() in ["true", "1", "yes"]

        # ✅ Save child
        child = serializer.save(tenant=tenant)

        # ✅ Handle parent account creation if requested
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
                role="parent",  # make sure you have this field
            )

            # ✅ Link created user to this child
            child.parent_user = user
            child.save()

            self.generated_username = username
            self.generated_password = password
        else:
            self.generated_username = None
            self.generated_password = None

    def create(self, request, *args, **kwargs):
        """Return username/password if a parent account was created."""
        response = super().create(request, *args, **kwargs)
        if self.generated_username:
            response.data["username"] = self.generated_username
            response.data["password"] = self.generated_password
        return response


# -----------------------------------------------------------
# 👶 CHILD DETAIL (GET / PUT / DELETE)
# -----------------------------------------------------------
class ChildDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Child.objects.filter(tenant=user.tenant)
            .select_related("classroom")
            .prefetch_related("clubs")
        )

        # ✅ Parents can only view/update their own child
        if user.role == "parent":
            return qs.filter(parent_user=user)
        return qs

# children/views.py
class MyChildView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Child.objects.get(parent_user=self.request.user)
