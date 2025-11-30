from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
import logging

from .models import DailyReport, ReportMedia
from .serializers import DailyReportSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from core.validators import validate_file_upload, MAX_FILE_SIZE
from core.permissions import IsTenantMember

logger = logging.getLogger("api")


class DailyReportListCreateView(generics.ListCreateAPIView):
    """✅ OPTIMIZED: Query optimization with select_related + prefetch_related"""

    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """✅ Prevent N+1 queries"""
        tenant = self.request.user.tenant
        queryset = (
            DailyReport.objects.filter(tenant=tenant)
            .select_related("child")  # ✅ FK optimization
            .prefetch_related("media_files")  # ✅ Related media optimization
        )

        # Filter by child if provided
        child_id = self.request.query_params.get("child")
        if child_id:
            queryset = queryset.filter(child_id=child_id)

        return queryset

    @transaction.atomic  # ✅ Ensure atomic operations
    def perform_create(self, serializer):
        """Create report and handle media files atomically"""
        try:
            tenant = self.request.user.tenant
            submitted_by = (
                self.request.user.get_full_name() or self.request.user.username
            )

            report = serializer.save(
                tenant=tenant,
                submitted_by=submitted_by,
            )
            logger.info(f"Created report for child {report.child_id} by {submitted_by}")

            # Handle attached media files
            files = self.request.FILES.getlist("media_files")
            if files:
                logger.info(f"Processing {len(files)} media files")

                for f in files:
                    try:
                        validate_file_upload(
                            f,
                            max_size=MAX_FILE_SIZE,
                            allowed_types={
                                "image/jpeg",
                                "image/png",
                                "image/gif",
                                "video/mp4",
                                "video/quicktime",
                            },
                        )
                        ReportMedia.objects.create(report=report, file=f, tenant=tenant)
                    except Exception as e:
                        logger.warning(f"Failed to save media file: {e}")

        except Exception as e:
            logger.error(f"Error creating report: {e}", exc_info=True)
            raise

    def create(self, request, *args, **kwargs):
        """Override to handle multipart and JSON uploads"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Create error: {e}")
            return Response(
                {"error": "Failed to create report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DailyReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """✅ OPTIMIZED: Retrieve, update or delete report"""

    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ Optimized for single report"""
        return (
            DailyReport.objects.filter(tenant=self.request.user.tenant)
            .select_related("child")
            .prefetch_related("media_files")
        )
