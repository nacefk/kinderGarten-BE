from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
import logging

from .models import Event, WeeklyPlan
from .serializers import EventSerializer, WeeklyPlanSerializer
from core.permissions import IsTenantMember

logger = logging.getLogger("api")


# -------- Event ViewSet --------
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ OPTIMIZED: Filtered by tenant and classroom"""
        queryset = (
            Event.objects.filter(tenant=self.request.user.tenant)
            .select_related("classroom")  # ✅ FK optimization
            .order_by("date")
        )

        classroom_id = self.request.query_params.get("classroom")
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)

        return queryset


# -------- Weekly Plan ViewSet --------
class WeeklyPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyPlanSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ OPTIMIZED: Filtered by tenant"""
        queryset = (
            WeeklyPlan.objects.filter(tenant=self.request.user.tenant)
            .select_related("classroom")  # ✅ FK optimization
            .order_by("day", "time")
        )

        classroom_id = self.request.query_params.get("classroom")
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)

        return queryset

    @transaction.atomic  # ✅ Atomic operations
    def create(self, request, *args, **kwargs):
        """✅ IMPROVED: Better error handling with logging"""
        try:
            logger.info(f"📥 Creating WeeklyPlan: {request.data}")

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"❌ Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            logger.info(f"✅ WeeklyPlan created successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"💥 Exception during WeeklyPlan save: {e}", exc_info=True)
            return Response(
                {"error": "Failed to create plan"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
