from datetime import date
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import AttendanceRecord, ExtraHourRequest
from .serializers import AttendanceRecordSerializer, ExtraHourRequestSerializer


class AttendanceSummaryView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
        tenant = self.request.user.tenant
        today = date.today()
        return AttendanceRecord.objects.filter(tenant=tenant, date=today)


class AttendanceBulkUpdateView(generics.GenericAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tenant = request.user.tenant
        today = date.today()
        records = request.data.get("records", [])

        created = []
        for rec in records:
            child_id = rec.get("child")
            status_value = rec.get("status", "present")

            record, _ = AttendanceRecord.objects.update_or_create(
                tenant=tenant,
                child_id=child_id,
                date=today,
                defaults={"status": status_value},  # ✅ no "time"
            )
            created.append(record)

        serializer = self.get_serializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExtraHourPendingListView(generics.ListAPIView):
    serializer_class = ExtraHourRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = self.request.user.tenant
        return ExtraHourRequest.objects.filter(tenant=tenant, status="pending")
