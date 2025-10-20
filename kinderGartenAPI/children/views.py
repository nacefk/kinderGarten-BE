from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from children.models import Child
from planning.models import ClassRoom
from children.serializers import ChildSerializer, ClassRoomSerializer

User = get_user_model()


class ClassRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClassRoom.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class ChildListCreateView(generics.ListCreateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = self.request.user.tenant
        classroom_id = self.request.query_params.get("classroom_id")
        qs = Child.objects.filter(tenant=tenant)
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return qs

    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        child = serializer.save(tenant=tenant)

        # ✅ Only generate credentials if has_mobile_app=True
        has_mobile_app = (
    self.request.data.get("has_mobile_app")
    or self.request.data.get("hasMobileApp")
    or False
)

        if str(has_mobile_app).lower() in ["true", "1", "yes"]:
            from django.utils.text import slugify
            from django.utils.crypto import get_random_string
            from django.contrib.auth import get_user_model

            User = get_user_model()

            base_username = slugify(child.name)
            username = base_username
            if User.objects.filter(username=username).exists():
                username = f"{base_username}_{get_random_string(3).lower()}"

            password = get_random_string(
                8,
                allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
            )

            user = User.objects.create_user(
                username=username,
                password=password,
                tenant=tenant,
                first_name=child.name,
            )

            if hasattr(child, "user"):
                child.user = user
                child.save()

            # Store generated credentials for response
            self.generated_username = username
            self.generated_password = password
        else:
            self.generated_username = None
            self.generated_password = None

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if self.generated_username:
            response.data["username"] = self.generated_username
            response.data["password"] = self.generated_password
        return response


class ChildDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(tenant=self.request.user.tenant)
