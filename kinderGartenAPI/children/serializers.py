from rest_framework import serializers
from django.contrib.auth import get_user_model
from children.models import Child, Club
from .models import ClassRoom

User = get_user_model()


# -----------------------------------------------------------
# 🏫 CLASSROOM SERIALIZER (for nested read)
# -----------------------------------------------------------
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
        read_only_fields = ["tenant"]


# -----------------------------------------------------------
# 🎨 CLUB SERIALIZER
# -----------------------------------------------------------
class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = "__all__"
        read_only_fields = ["tenant"]


# -----------------------------------------------------------
# 👤 PARENT USER SERIALIZER (minimal info)
# -----------------------------------------------------------
class ParentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "email"]
        read_only_fields = fields


# -----------------------------------------------------------
# 👶 CHILD SERIALIZER
# -----------------------------------------------------------
class ChildSerializer(serializers.ModelSerializer):
    # ✅ Read-only related data
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    teacher_name = serializers.CharField(source="classroom.teacher_name", read_only=True)

    # ✅ Many-to-many relationship for clubs
    clubs = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
    )
    club_details = ClubSerializer(source="clubs", many=True, read_only=True)

    # ✅ Linked parent user (read-only)
    parent_user = ParentUserSerializer(read_only=True)

    # ✅ Frontend alias for consistency
    has_mobile_app = serializers.BooleanField(write_only=True, required=False, default=False)

    # ✅ Write-friendly classroom
    classroom_id = serializers.PrimaryKeyRelatedField(
        source="classroom",
        queryset=ClassRoom.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "birthdate",
            "gender",
            "classroom",
            "classroom_id",
            "classroom_name",
            "clubs",
            "club_details",
            "parent_user",
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
        read_only_fields = ["tenant", "parent_user"]

    def update(self, instance, validated_data):
        """Prevent tenants and parent_user from being altered directly."""
        validated_data.pop("tenant", None)
        validated_data.pop("parent_user", None)
        return super().update(instance, validated_data)
