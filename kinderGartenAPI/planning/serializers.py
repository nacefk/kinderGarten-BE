from rest_framework import serializers
from .models import WeeklyPlan, Event
from children.models import ClassRoom
from children.serializers import ClassRoomSerializer


# -------- Event Serializer --------
class EventSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.none(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    apply_to_all_classes = serializers.BooleanField(
        write_only=True, default=False, required=False
    )
    classroom_detail = ClassRoomSerializer(source="classroom", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "classroom",
            "apply_to_all_classes",
            "classroom_detail",
        ]
        read_only_fields = ["tenant"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Dynamically set tenant-filtered queryset
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            tenant = request.user.tenant
            self.fields["classroom"].queryset = ClassRoom.objects.filter(tenant=tenant)

    def validate(self, data):
        """If no classroom provided, default to all classrooms"""
        classroom = data.get("classroom")
        apply_to_all = data.get("apply_to_all_classes", False)

        # If no classroom ID and not explicitly set to false, default to all classes
        if not classroom:
            data["apply_to_all_classes"] = True

        return data

    def to_internal_value(self, data):
        """Handle both 'classroom' and 'classroom_id' field names"""
        # If classroom_id is sent, rename it to classroom
        if "classroom_id" in data and "classroom" not in data:
            data = data.copy()
            data["classroom"] = data.pop("classroom_id")
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Remove apply_to_all_classes from validated_data before creating the event"""
        # Pop the apply_to_all_classes field since it's not a model field
        validated_data.pop("apply_to_all_classes", None)
        return super().create(validated_data)


# -------- Weekly Plan Serializer --------
class WeeklyPlanSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.none(), write_only=True
    )
    classroom_detail = ClassRoomSerializer(source="classroom", read_only=True)

    class Meta:
        model = WeeklyPlan
        fields = ["id", "title", "day", "time", "classroom", "classroom_detail"]
        read_only_fields = ["tenant"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Dynamically set tenant-filtered queryset
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            tenant = request.user.tenant
            self.fields["classroom"].queryset = ClassRoom.objects.filter(tenant=tenant)
