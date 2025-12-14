from rest_framework import generics, permissions, status, serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.db.utils import IntegrityError
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
            .order_by("-created_at")  # ✅ Order by latest first
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

        except IntegrityError as e:
            if "unique constraint" in str(e) and "child_id" in str(e):
                logger.warning(f"Child already has a report: {e}")
                raise serializers.ValidationError(
                    {
                        "child": "This child already has a report. Update the existing one instead."
                    }
                )
            raise
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
        except serializers.ValidationError as e:
            logger.warning(f"Validation error: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Create error: {e}")
            return Response(
                {"error": "Failed to create report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DailyReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """✅ OPTIMIZED: Retrieve, update or delete report"""

    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ Optimized for single report"""
        return (
            DailyReport.objects.filter(tenant=self.request.user.tenant)
            .select_related("child")
            .prefetch_related("media_files")
            .order_by("-created_at")  # ✅ Order by latest first
        )

    @transaction.atomic
    def perform_update(self, serializer):
        """Update report and handle new media files"""
        try:
            report = serializer.save()
            logger.info(f"Updated report {report.id}")

            # Handle new media files if provided
            files = self.request.FILES.getlist("media_files")
            if files:
                logger.info(
                    f"Adding {len(files)} new media files to report {report.id}"
                )

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
                        ReportMedia.objects.create(
                            report=report, file=f, tenant=report.tenant
                        )
                    except Exception as e:
                        logger.warning(f"Failed to save media file: {e}")

        except Exception as e:
            logger.error(f"Error updating report: {e}", exc_info=True)
            raise

    def update(self, request, *args, **kwargs):
        """Handle both partial and full updates with media"""
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Update error: {e}")
            return Response(
                {"error": "Failed to update report"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReportMediaDeleteView(generics.DestroyAPIView):
    """Delete a specific media file from a report"""

    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """Only allow deletion of media files from the user's tenant"""
        return ReportMedia.objects.filter(tenant=self.request.user.tenant)

    def perform_destroy(self, instance):
        """Delete media file"""
        report_id = instance.report.id
        logger.info(f"Deleting media file {instance.id} from report {report_id}")

        # Delete the file from storage
        if instance.file:
            instance.file.delete(save=False)

        instance.delete()
        logger.info(f"Deleted media file {instance.id}")

    def destroy(self, request, *args, **kwargs):
        """Override to return empty response on delete"""
        try:
            self.perform_destroy(self.get_object())
            return Response(
                {"message": "Media file deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return Response(
                {"error": "Failed to delete media file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
