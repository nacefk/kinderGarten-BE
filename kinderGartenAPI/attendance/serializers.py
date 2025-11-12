# attendance/serializers.py
from rest_framework import serializers
from .models import AttendanceRecord, ExtraHourRequest

class AttendanceRecordSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ["id", "child", "child_name", "date", "status"]


class ExtraHourRequestSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)

    class Meta:
        model = ExtraHourRequest
        fields = ["id", "child", "child_name", "start", "end", "status"]
