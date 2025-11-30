from rest_framework import serializers
from .models import WeeklyPlan, Event
from children.models import ClassRoom
from children.serializers import ClassRoomSerializer


# -------- Event Serializer --------
class EventSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.none(), write_only=True
    )
    classroom_detail = ClassRoomSerializer(source="classroom", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "title", "description", "date", "classroom", "classroom_detail"]
        read_only_fields = ["tenant"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Dynamically set tenant-filtered queryset
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            tenant = request.user.tenant
            self.fields["classroom"].queryset = ClassRoom.objects.filter(tenant=tenant)


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
