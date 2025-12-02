from datetime import date
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
import logging

from .models import AttendanceRecord, ExtraHourRequest
from .serializers import AttendanceRecordSerializer, ExtraHourRequestSerializer
from children.models import Child
from core.permissions import IsTenantAdmin

logger = logging.getLogger("api")


class AttendanceSummaryView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttendanceRecordSerializer  # For schema generation

    def get(self, request):
        """Get today's attendance summary"""
        tenant = request.user.tenant
        today = date.today()

        total_present = AttendanceRecord.objects.filter(
            tenant=tenant, date=today, status="present"
        ).count()
        total_absent = AttendanceRecord.objects.filter(
            tenant=tenant, date=today, status="absent"
        ).count()

        return Response({"present": total_present, "absent": total_absent})


class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """✅ OPTIMIZED: select_related for child optimization"""
        tenant = self.request.user.tenant
        today = date.today()
        return AttendanceRecord.objects.filter(
            tenant=tenant, date=today
        ).select_related(
            "child"
        )  # ✅ FK optimization


class AttendanceBulkUpdateView(generics.GenericAPIView):
    """✅ SECURE: Bulk attendance update with validation"""

    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]

    @transaction.atomic  # ✅ Atomic operation
    def post(self, request, *args, **kwargs):
        tenant = request.user.tenant
        today = date.today()
        records_data = request.data.get("records", [])

        if not records_data:
            return Response(
                {"error": "No records provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        try:
            for rec_data in records_data:
                child_id = rec_data.get("child_id") or rec_data.get("child")
                status_value = rec_data.get("status", "present")

                # ✅ VALIDATE: child belongs to tenant
                if not Child.objects.filter(id=child_id, tenant=tenant).exists():
                    return Response(
                        {"error": f"Child {child_id} not found in your tenant"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                record, _ = AttendanceRecord.objects.update_or_create(
                    tenant=tenant,
                    child_id=child_id,
                    date=today,
                    defaults={"status": status_value},
                )
                created.append(record)

            serializer = self.get_serializer(created, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in bulk attendance update: {e}", exc_info=True)
            return Response(
                {"error": "Failed to update attendance"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ExtraHourPendingListView(generics.ListAPIView):
    serializer_class = ExtraHourRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]

    def get_queryset(self):
        """✅ OPTIMIZED: select_related for child"""
        tenant = self.request.user.tenant
        return ExtraHourRequest.objects.filter(
            tenant=tenant, status="pending"
        ).select_related(
            "child"
        )  # ✅ FK optimization


class ExtraHourCreateView(generics.CreateAPIView):
    serializer_class = ExtraHourRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        serializer.save(tenant=tenant, status="pending")


class ExtraHourApproveRejectView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]
    serializer_class = ExtraHourRequestSerializer  # For schema generation

    def post(self, request, pk):
        """Approve or reject an extra hour request"""
        action = request.data.get("action")

        if action not in ["approved", "rejected"]:
            return Response(
                {"error": "Invalid action. Must be 'approved' or 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        req = get_object_or_404(ExtraHourRequest, pk=pk, tenant=request.user.tenant)

        req.status = action
        req.save()

        logger.info(f"Extra hour request {pk} {action} by {request.user.username}")

        return Response({"success": True, "status": req.status})


class ExtraHourRequestCreateView(generics.CreateAPIView):
    """Alternative endpoint for creating extra hour requests"""

    serializer_class = ExtraHourRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        serializer.save(tenant=tenant, status="pending")


class ExtraHourMyRequestsListView(generics.ListAPIView):
    """Parents can view their own extra hour requests and their status"""

    serializer_class = ExtraHourRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get extra hour requests for the current parent's children"""
        from children.models import Child

        tenant = self.request.user.tenant
        user = self.request.user

        # Get all children associated with this parent
        children = Child.objects.filter(tenant=tenant, parent_user=user)

        # Get all extra hour requests for those children
        return (
            ExtraHourRequest.objects.filter(tenant=tenant, child__in=children)
            .select_related("child")
            .order_by("-created_at")
        )
