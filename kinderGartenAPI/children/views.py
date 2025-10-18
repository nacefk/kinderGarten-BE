from rest_framework import viewsets
from core.mixins import TenantSaveMixin
from core.permissions import IsTenantStaffOrReadOnly
from .models import Child, ClassRoom
from .serializers import ChildSerializer, ClassRoomSerializer

class ClassRoomViewSet(TenantSaveMixin, viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsTenantStaffOrReadOnly]

class ChildViewSet(TenantSaveMixin, viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = [IsTenantStaffOrReadOnly]
