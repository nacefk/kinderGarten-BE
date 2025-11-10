from rest_framework import serializers
from .models import DailyReport, ReportMedia


class ReportMediaSerializer(serializers.ModelSerializer):
    # Return full URL (not relative path)
    file = serializers.FileField(use_url=True)

    class Meta:
        model = ReportMedia
        fields = ["id", "file", "uploaded_at"]


class DailyReportSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    media_files = ReportMediaSerializer(many=True, read_only=True)

    class Meta:
        model = DailyReport
        fields = "__all__"
        read_only_fields = ["tenant", "submitted_by"]
