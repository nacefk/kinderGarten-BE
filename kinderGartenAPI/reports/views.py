from rest_framework import generics, permissions
from .models import DailyReport
from .serializers import DailyReportSerializer

class DailyReportListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = self.request.user.tenant
        queryset = DailyReport.objects.filter(tenant=tenant)

        # Optional filtering
        child_id = self.request.query_params.get("child")
        if child_id:
            queryset = queryset.filter(child_id=child_id)


        return queryset

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.tenant,
            submitted_by=self.request.user.get_full_name() or self.request.user.username,
        )
class DailyReportDetailView(generics.RetrieveAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyReport.objects.filter(tenant=self.request.user.tenant)
