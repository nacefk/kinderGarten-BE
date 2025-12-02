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

    @transaction.atomic  # ✅ Atomic operations
    def create(self, request, *args, **kwargs):
        """✅ Create event for specific class or all classes"""
        try:
            logger.info(f"📥 Creating Event: {request.data}")

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"❌ Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Check validated_data for apply_to_all_classes flag
            apply_to_all = serializer.validated_data.get("apply_to_all_classes", False)

            if apply_to_all:
                # Create event for all classrooms in the tenant
                tenant = request.user.tenant
                from children.models import ClassRoom

                classrooms = ClassRoom.objects.filter(tenant=tenant)

                events = []
                for classroom in classrooms:
                    event = Event.objects.create(
                        title=serializer.validated_data["title"],
                        description=serializer.validated_data.get("description", ""),
                        date=serializer.validated_data["date"],
                        classroom=classroom,
                        tenant=tenant,
                    )
                    events.append(event)

                logger.info(f"✅ Created {len(events)} events for all classrooms")
                return Response(
                    {
                        "message": f"Event created for {len(events)} classrooms",
                        "count": len(events),
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                # Create event for specific classroom
                self.perform_create(serializer)
                logger.info(
                    f"✅ Event created successfully for classroom {serializer.validated_data['classroom'].id}"
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"💥 Exception during Event save: {e}", exc_info=True)
            return Response(
                {"error": "Failed to create event"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def perform_create(self, serializer):
        """Save event with tenant"""
        serializer.save(tenant=self.request.user.tenant)


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
