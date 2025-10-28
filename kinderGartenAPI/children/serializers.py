from rest_framework import serializers
from children.models import Child, Club
from .models import ClassRoom


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
        read_only_fields = ["tenant"]  # ✅ tenant handled automatically


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = "__all__"
        read_only_fields = ["tenant"]  # ✅ tenant handled automatically


class ChildSerializer(serializers.ModelSerializer):
    # ✅ Automatically include classroom name in responses
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    teacher_name = serializers.CharField(source="classroom.teacher_name", read_only=True)


    # ✅ Many-to-many relationship for clubs
    clubs = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
    )

    # ✅ Optional nested read-only club details
    club_details = ClubSerializer(source="clubs", many=True, read_only=True)

    # ✅ Allow frontend to send hasMobileApp / has_mobile_app temporarily
    has_mobile_app = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "birthdate",
            "gender",
            "classroom",
            "classroom_name",
            "clubs",
            "club_details",  # ✅ nested club data
            "parent_name",
            "avatar",
            "allergies",
            "conditions",
            "medication",
            "doctor",
            "weight",
            "height",
            "emergency_contact_name",
            "emergency_contact_relation",
            "emergency_contact_phone",
            "responsible_name",
            "responsible_phone",
            "teacher_name",
            "next_payment_date",
            "has_mobile_app",

        ]
        read_only_fields = ["tenant"]
