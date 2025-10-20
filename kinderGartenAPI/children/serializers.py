# children/serializers.py
from rest_framework import serializers
from children.models import Child
from planning.models import ClassRoom


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = [
            "id",
            "name",
            "teacher_name",
            "assistant_name",
            "age_range",
            "room",
            "students_count",
        ]


class ChildSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(
        source="classroom.name", read_only=True
    )

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "birthdate",
            "parent_name",
            "avatar",
            "classroom",
            "classroom_name",
        ]
