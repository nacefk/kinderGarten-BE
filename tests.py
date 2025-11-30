"""
Comprehensive unit tests for the refactored Django project
Tests cover: views, serializers, models, permissions, validators
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from core.models import Tenant, BaseTenantModel
from children.models import Child, ClassRoom, Club
from attendance.models import AttendanceRecord, ExtraHourRequest
from reports.models import DailyReport, ReportMedia
from chat.models import Conversation, Message
from core.permissions import IsTenantAdmin, IsTenantParent, IsTenantMember
from core.validators import validate_file_upload
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


# ============================================================================
# FIXTURES & SETUP
# ============================================================================


@pytest.fixture
def tenant():
    """Create a test tenant"""
    return Tenant.objects.create(name="Test Kindergarten", slug="test-kindergarten")


@pytest.fixture
def admin_user(tenant):
    """Create an admin user"""
    return User.objects.create_user(
        username="admin", password="testpass123", tenant=tenant, role="admin"
    )


@pytest.fixture
def parent_user(tenant):
    """Create a parent user"""
    return User.objects.create_user(
        username="parent1", password="testpass123", tenant=tenant, role="parent"
    )


@pytest.fixture
def other_tenant():
    """Create a different tenant"""
    return Tenant.objects.create(name="Other Kindergarten", slug="other-kindergarten")


@pytest.fixture
def other_admin(other_tenant):
    """Create admin in other tenant"""
    return User.objects.create_user(
        username="other_admin",
        password="testpass123",
        tenant=other_tenant,
        role="admin",
    )


@pytest.fixture
def classroom(tenant):
    """Create a classroom"""
    return ClassRoom.objects.create(
        tenant=tenant, name="Class A", teacher_name="John Doe"
    )


@pytest.fixture
def child(tenant, parent_user, classroom):
    """Create a child"""
    return Child.objects.create(
        tenant=tenant,
        name="Test Child",
        parent_name="Parent Name",
        parent_user=parent_user,
        classroom=classroom,
    )


# ============================================================================
# PERMISSION TESTS
# ============================================================================


@pytest.mark.django_db
class TestPermissions:
    """Test permission classes"""

    def test_is_tenant_admin_permission(self, admin_user, parent_user):
        """Test IsTenantAdmin permission"""
        permission = IsTenantAdmin()

        # Admin should have permission
        assert permission.has_permission(None, admin_user) == True

        # Parent should not have permission
        assert permission.has_permission(None, parent_user) == False

    def test_is_tenant_parent_permission(self, admin_user, parent_user):
        """Test IsTenantParent permission"""
        permission = IsTenantParent()

        # Parent should have permission
        assert permission.has_permission(None, parent_user) == True

        # Admin should not have permission
        assert permission.has_permission(None, admin_user) == False

    def test_tenant_member_permission(self, parent_user, child):
        """Test IsTenantMember permission"""
        permission = IsTenantMember()

        # Same tenant should have permission
        assert permission.has_object_permission(None, None, child, parent_user) == True


# ============================================================================
# VALIDATOR TESTS
# ============================================================================


@pytest.mark.django_db
class TestValidators:
    """Test file validators"""

    def test_validate_file_upload_size(self):
        """Test file size validation"""
        # Create a file that's too large
        large_file = SimpleUploadedFile(
            "test.jpg", b"x" * (11 * 1024 * 1024), content_type="image/jpeg"  # 11MB
        )

        with pytest.raises(ValidationError):
            validate_file_upload(large_file, max_size=5 * 1024 * 1024)

    def test_validate_file_upload_extension(self):
        """Test file extension validation"""
        # Create a file with invalid extension
        invalid_file = SimpleUploadedFile(
            "test.exe", b"invalid content", content_type="application/x-msdownload"
        )

        with pytest.raises(ValidationError):
            validate_file_upload(invalid_file)

    def test_validate_file_upload_mime_type(self):
        """Test MIME type validation"""
        # Create a file with invalid MIME type
        invalid_file = SimpleUploadedFile(
            "test.jpg", b"invalid content", content_type="application/x-msdownload"
        )

        with pytest.raises(ValidationError):
            validate_file_upload(invalid_file)

    def test_validate_file_upload_success(self):
        """Test successful file validation"""
        valid_file = SimpleUploadedFile(
            "test.jpg", b"\xff\xd8\xff\xe0", content_type="image/jpeg"  # JPEG header
        )

        assert validate_file_upload(valid_file) == True


# ============================================================================
# MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestModels:
    """Test model behavior"""

    def test_attendance_record_unique_constraint(self, tenant, child):
        """Test unique constraint on attendance record"""
        today = date.today()

        # Create first record
        AttendanceRecord.objects.create(
            tenant=tenant, child=child, date=today, status="present"
        )

        # Try to create duplicate - should update instead
        record2, created = AttendanceRecord.objects.update_or_create(
            tenant=tenant, child=child, date=today, defaults={"status": "absent"}
        )

        assert created == False
        assert record2.status == "absent"

    def test_attendance_record_future_date_validation(self, tenant, child):
        """Test that future dates are rejected"""
        from django.utils import timezone

        future_date = timezone.now().date() + timedelta(days=1)
        record = AttendanceRecord(
            tenant=tenant, child=child, date=future_date, status="present"
        )

        with pytest.raises(ValidationError):
            record.full_clean()

    def test_conversation_unique_constraint(self, tenant, admin_user, parent_user):
        """Test unique constraint on conversations"""
        # Create first conversation
        conv1 = Conversation.objects.create(
            tenant=tenant, parent=parent_user, admin=admin_user
        )

        # Try to create duplicate - should fail
        with pytest.raises(Exception):  # IntegrityError
            Conversation.objects.create(
                tenant=tenant, parent=parent_user, admin=admin_user
            )


# ============================================================================
# VIEW TESTS
# ============================================================================


@pytest.mark.django_db
class TestChildrenViews(APITestCase):
    """Test children app views"""

    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Org", slug="test-org")
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", tenant=self.tenant, role="admin"
        )
        self.parent_user = User.objects.create_user(
            username="parent", password="testpass123", tenant=self.tenant, role="parent"
        )
        self.classroom = ClassRoom.objects.create(tenant=self.tenant, name="Class A")
        self.client = APIClient()

    def test_child_list_admin_gets_all_children(self):
        """Admin should see all children"""
        # Create children
        Child.objects.create(
            tenant=self.tenant,
            name="Child 1",
            parent_name="Parent 1",
            classroom=self.classroom,
        )
        Child.objects.create(
            tenant=self.tenant,
            name="Child 2",
            parent_name="Parent 2",
            classroom=self.classroom,
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/children/")

        assert response.status_code == status.HTTP_200_OK
        # Pagination - check results count
        assert len(response.data["results"]) == 2

    def test_child_list_parent_sees_only_own_child(self):
        """Parent should only see their own child"""
        child = Child.objects.create(
            tenant=self.tenant,
            name="My Child",
            parent_name="Me",
            parent_user=self.parent_user,
            classroom=self.classroom,
        )

        self.client.force_authenticate(user=self.parent_user)
        response = self.client.get("/api/children/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_child_list_tenant_isolation(self):
        """Users from different tenants shouldn't see each other's data"""
        # Create another tenant and user
        other_tenant = Tenant.objects.create(name="Other Org", slug="other-org")
        other_admin = User.objects.create_user(
            username="other_admin",
            password="testpass123",
            tenant=other_tenant,
            role="admin",
        )

        # Create child in first tenant
        Child.objects.create(
            tenant=self.tenant,
            name="My Child",
            parent_name="Me",
            classroom=self.classroom,
        )

        # Other tenant admin should see nothing
        self.client.force_authenticate(user=other_admin)
        response = self.client.get("/api/children/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestAttendanceViews(APITestCase):
    """Test attendance views"""

    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Org", slug="test-org")
        self.admin_user = User.objects.create_user(
            username="admin", password="testpass123", tenant=self.tenant, role="admin"
        )
        self.classroom = ClassRoom.objects.create(tenant=self.tenant, name="Class A")
        self.child = Child.objects.create(
            tenant=self.tenant,
            name="Test Child",
            parent_name="Parent",
            classroom=self.classroom,
        )
        self.client = APIClient()

    def test_bulk_attendance_update_validates_child_tenant(self):
        """Bulk update should validate child belongs to tenant"""
        other_tenant = Tenant.objects.create(name="Other", slug="other")
        other_child = Child.objects.create(
            tenant=other_tenant,
            name="Other Child",
            parent_name="Other Parent",
            classroom=ClassRoom.objects.create(tenant=other_tenant, name="Class"),
        )

        self.client.force_authenticate(user=self.admin_user)

        data = {"records": [{"child_id": other_child.id, "status": "present"}]}

        response = self.client.post("/api/attendance/update/", data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# SERIALIZER TESTS
# ============================================================================


@pytest.mark.django_db
class TestSerializers:
    """Test serializers"""

    def test_child_serializer_tenant_filtered_clubs(self, tenant, child):
        """Child serializer should only show tenant's clubs"""
        from children.serializers import ChildSerializer
        from rest_framework.test import APIRequestFactory

        # Create clubs in different tenants
        club_same = Club.objects.create(tenant=tenant, name="Club Same")
        other_tenant = Tenant.objects.create(name="Other", slug="other")
        club_other = Club.objects.create(tenant=other_tenant, name="Club Other")

        # Add same-tenant club
        child.clubs.add(club_same)

        # Test serializer
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = User.objects.create_user(
            username="user", password="pass", tenant=tenant, role="admin"
        )

        serializer = ChildSerializer(child, context={"request": request})

        # Should only contain same-tenant club
        assert len(serializer.data["club_details"]) == 1
        assert serializer.data["club_details"][0]["name"] == "Club Same"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.django_db
class TestIntegration:
    """Integration tests for complete workflows"""

    def test_child_creation_with_parent_user(self, tenant, admin_user):
        """Test creating child with parent user account"""
        from django.db import transaction
        from children.views import ChildListCreateView
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.post(
            "/api/children/",
            {"name": "New Child", "parent_name": "Parent", "has_mobile_app": True},
            format="json",
        )
        request.user = admin_user

        view = ChildListCreateView.as_view()

        # Should create child and parent user
        with transaction.atomic():
            response = view(request)

        # Verify child was created
        child = Child.objects.filter(name="New Child").first()
        assert child is not None
        assert child.parent_user is not None
        assert child.parent_user.role == "parent"
