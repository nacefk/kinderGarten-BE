from rest_framework import serializers
from .models import Tenant, User, ClassRoom, Child, DailyReport, Event, PlanActivity, AttendanceRecord, ExtraHourRequest
from django.contrib.auth.hashers import make_password

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "tenant", "password"]
        read_only_fields = ["tenant"]

    def create(self, validated):
        # password optional → generate or hash
        pwd = validated.pop("password", None) or User.objects.make_random_password()
        validated["password"] = make_password(pwd)
        return super().create(validated)


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = "__all__"
        read_only_fields = ["tenant"]


class ChildSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = Child
        fields = ["id", "name", "birthdate", "classroom", "classroom_name", "parent_name", "avatar", "tenant"]
        read_only_fields = ["tenant"]


class DailyReportSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    class Meta:
        model = DailyReport
        fields = "__all__"
        read_only_fields = ["tenant"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["tenant"]


class PlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanActivity
        fields = "__all__"
        read_only_fields = ["tenant"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    class Meta:
        model = AttendanceRecord
        fields = "__all__"
        read_only_fields = ["tenant"]


class ExtraHourRequestSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    class Meta:
        model = ExtraHourRequest
        fields = "__all__"
        read_only_fields = ["tenant"]
