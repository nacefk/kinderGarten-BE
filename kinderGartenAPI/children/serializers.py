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
        read_only_fields = ["tenant"]  # ✅ tenant handled automatically


class ChildSerializer(serializers.ModelSerializer):
    # ✅ Automatically include classroom name in responses
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

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
            "next_payment_date",
            "has_mobile_app",  # ✅ include extra field here
        ]
        read_only_fields = ["tenant"]  # ✅ prevents validation error
