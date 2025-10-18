from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from children.models import Child
from planning.models import ClassRoom
from children.serializers import ChildSerializer,ClassRoomSerializer



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
        serializer.save(tenant=self.request.user.tenant)
