from rest_framework import serializers
from django.contrib.auth import get_user_model
from children.models import Child, Club
from .models import ClassRoom

User = get_user_model()


# -----------------------------------------------------------
# 🏫 CLASSROOM SERIALIZER
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
# 👤 PARENT USER SERIALIZER
# -----------------------------------------------------------
class ParentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "email"]
        read_only_fields = fields


# -----------------------------------------------------------
# 👶 CHILD LIST SERIALIZER (Lightweight for listings)
# -----------------------------------------------------------
class ChildListSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(
        source="classroom.name", read_only=True, allow_null=True
    )
    parent_user_name = serializers.CharField(
        source="parent_user.username", read_only=True, allow_null=True
    )

    class Meta:
        model = Child
        fields = [
            "id",
            "name",
            "gender",
            "birthdate",
            "classroom_name",
            "parent_name",
            "avatar",
            "parent_user_name",
        ]
        read_only_fields = ["tenant"]


# -----------------------------------------------------------
# 👶 CHILD DETAIL SERIALIZER (Full data)
# -----------------------------------------------------------
class ChildSerializer(serializers.ModelSerializer):
    # ✅ Read-only related data
    classroom_name = serializers.CharField(
        source="classroom.name", read_only=True, allow_null=True
    )
    teacher_name = serializers.CharField(
        source="classroom.teacher_name", read_only=True, allow_null=True
    )

    # ✅ Tenant-filtered many-to-many relationship for clubs
    clubs = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.none(),
        many=True,
        required=False,
        allow_empty=True,
    )
    club_details = ClubSerializer(source="clubs", many=True, read_only=True)

    # ✅ Linked parent user (read-only)
    parent_user = ParentUserSerializer(read_only=True)

    # ✅ Frontend alias for consistency
    has_mobile_app = serializers.BooleanField(
        write_only=True, required=False, default=False
    )

    # ✅ Write-friendly classroom
    classroom_id = serializers.PrimaryKeyRelatedField(
        source="classroom",
        queryset=ClassRoom.objects.none(),
        write_only=True,
        required=False,
        allow_null=True,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Dynamically set tenant-filtered querysets
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            tenant = request.user.tenant
            self.fields["clubs"].queryset = Club.objects.filter(tenant=tenant)
            self.fields["classroom_id"].queryset = ClassRoom.objects.filter(
                tenant=tenant
            )

    def update(self, instance, validated_data):
        """Prevent tenants and parent_user from being altered"""
        validated_data.pop("tenant", None)
        validated_data.pop("parent_user", None)
        return super().update(instance, validated_data)
