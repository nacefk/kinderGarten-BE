from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import DailyReport, ReportMedia
from .serializers import DailyReportSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class DailyReportListCreateView(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = self.request.user.tenant
        queryset = DailyReport.objects.filter(tenant=tenant)

        # Optional filter by child
        child_id = self.request.query_params.get("child")
        if child_id:
            queryset = queryset.filter(child_id=child_id)

        return queryset

    def perform_create(self, serializer):
        child_id = self.request.data.get("child")
        if isinstance(child_id, str) and child_id.isdigit():
            self.request.data._mutable = True  # allow editing QueryDict
            self.request.data["child"] = int(child_id)
            self.request.data._mutable = False

        report = serializer.save(
            tenant=self.request.user.tenant,
            submitted_by=self.request.user.get_full_name() or self.request.user.username,
        )

        # ✅ Handle attached media files
        files = self.request.FILES.getlist("media_files")
        print("📸 Received files:", len(files))

        for f in files:
            ReportMedia.objects.create(report=report, file=f, tenant=self.request.user.tenant)

        return report


    def create(self, request, *args, **kwargs):
        """Override to support multipart and JSON uploads"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = self.perform_create(serializer)
        return Response(DailyReportSerializer(report).data, status=status.HTTP_201_CREATED)


class DailyReportDetailView(generics.RetrieveAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyReport.objects.filter(tenant=self.request.user.tenant)
