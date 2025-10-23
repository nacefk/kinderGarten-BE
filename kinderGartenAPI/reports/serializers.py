from rest_framework import serializers
from .models import DailyReport

class DailyReportSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)

    class Meta:
        model = DailyReport
        fields = "__all__"
        read_only_fields = ["tenant", "submitted_by"]
