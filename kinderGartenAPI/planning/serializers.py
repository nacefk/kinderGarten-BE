from rest_framework import serializers
from .models import WeeklyPlan, Event
from children.models import ClassRoom
from children.serializers import ClassRoomSerializer


# -------- Event Serializer --------
class EventSerializer(serializers.ModelSerializer):
    class_name = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        write_only=True
    )
    class_name_detail = ClassRoomSerializer(source="class_name", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "title", "description", "date", "class_name", "class_name_detail"]


# -------- Weekly Plan Serializer --------
class WeeklyPlanSerializer(serializers.ModelSerializer):
    class_name = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        write_only=True
    )
    class_name_detail = ClassRoomSerializer(source="class_name", read_only=True)

    class Meta:
        model = WeeklyPlan
        fields = ["id", "title", "day", "time", "class_name", "class_name_detail"]
