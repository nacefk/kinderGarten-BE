"""
Integration tests for complete multi-tenant workflows
Tests cover: tenant isolation, permission inheritance, cascading data
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from core.models import Tenant
from children.models import Child, ClassRoom, Club
from attendance.models import AttendanceRecord
from chat.models import Conversation, Message
from reports.models import DailyReport

User = get_user_model()


@pytest.mark.django_db
class TestMultiTenantIsolation(APITestCase):
    """Test that tenants are properly isolated"""

    def setUp(self):
        """Set up two complete tenant environments"""
        # Tenant 1
        self.tenant1 = Tenant.objects.create(name="Org 1", slug="org1")
        self.admin1 = User.objects.create_user(
            username="admin1", password="pass", tenant=self.tenant1, role="admin"
        )
        self.parent1 = User.objects.create_user(
            username="parent1", password="pass", tenant=self.tenant1, role="parent"
        )
        self.classroom1 = ClassRoom.objects.create(tenant=self.tenant1, name="Class A")
        self.child1 = Child.objects.create(
            tenant=self.tenant1,
            name="Child 1",
            parent_name="P1",
            parent_user=self.parent1,
            classroom=self.classroom1,
        )

        # Tenant 2
        self.tenant2 = Tenant.objects.create(name="Org 2", slug="org2")
        self.admin2 = User.objects.create_user(
            username="admin2", password="pass", tenant=self.tenant2, role="admin"
        )
        self.parent2 = User.objects.create_user(
            username="parent2", password="pass", tenant=self.tenant2, role="parent"
        )
        self.classroom2 = ClassRoom.objects.create(tenant=self.tenant2, name="Class B")
        self.child2 = Child.objects.create(
            tenant=self.tenant2,
            name="Child 2",
            parent_name="P2",
            parent_user=self.parent2,
            classroom=self.classroom2,
        )

        self.client = APIClient()

    def test_admin_cannot_see_other_tenant_children(self):
        """Admin1 should not see Child2"""
        self.client.force_authenticate(user=self.admin1)
        response = self.client.get("/api/children/")

        assert response.status_code == status.HTTP_200_OK
        child_ids = [c["id"] for c in response.data["results"]]
        assert self.child1.id in child_ids
        assert self.child2.id not in child_ids

    def test_parent_cannot_see_other_tenant_children(self):
        """Parent1 should not see Child2"""
        self.client.force_authenticate(user=self.parent1)
        response = self.client.get("/api/children/")

        assert response.status_code == status.HTTP_200_OK
        child_ids = [c["id"] for c in response.data["results"]]
        assert self.child1.id in child_ids
        assert self.child2.id not in child_ids

    def test_conversation_isolation(self):
        """Conversation between parent1/admin1 should not be visible to tenant2"""
        conv1 = Conversation.objects.create(
            tenant=self.tenant1, parent=self.parent1, admin=self.admin1
        )

        self.client.force_authenticate(user=self.admin2)
        response = self.client.get("/api/chat/conversations/")

        assert response.status_code == status.HTTP_200_OK
        conv_ids = [c["id"] for c in response.data["results"]]
        assert conv1.id not in conv_ids

    def test_attendance_isolation(self):
        """Attendance for child1 should not be visible to tenant2 admin"""
        att = AttendanceRecord.objects.create(
            tenant=self.tenant1, child=self.child1, date=date.today(), status="present"
        )

        self.client.force_authenticate(user=self.admin2)
        response = self.client.get(f"/api/attendance/records/")

        assert response.status_code == status.HTTP_200_OK
        att_ids = [a["id"] for a in response.data["results"]]
        assert att.id not in att_ids


@pytest.mark.django_db
class TestCascadingDataDeletion:
    """Test that deleting parent records properly cascades"""

    def test_deleting_classroom_cascades_to_children(self, tenant):
        """Deleting classroom should delete its children"""
        classroom = ClassRoom.objects.create(tenant=tenant, name="Temp Class")
        child = Child.objects.create(
            tenant=tenant, name="Child", parent_name="Parent", classroom=classroom
        )

        classroom.delete()

        assert Child.objects.filter(id=child.id).count() == 0

    def test_deleting_child_cascades_to_attendance(self, tenant, child):
        """Deleting child should cascade to attendance records"""
        att = AttendanceRecord.objects.create(
            tenant=tenant, child=child, date=date.today(), status="present"
        )

        child.delete()

        assert AttendanceRecord.objects.filter(id=att.id).count() == 0

    def test_deleting_parent_user_does_not_delete_child(self, tenant):
        """Deleting parent user should not delete child (soft reference)"""
        parent = User.objects.create_user(
            username="parent", password="pass", tenant=tenant, role="parent"
        )
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")
        child = Child.objects.create(
            tenant=tenant,
            name="Child",
            parent_name="Parent",
            parent_user=parent,
            classroom=classroom,
        )

        parent.delete()

        # Child should still exist but parent_user should be NULL
        child.refresh_from_db()
        assert child.parent_user is None


@pytest.mark.django_db
class TestAuthorizationWorkflows:
    """Test complete authorization scenarios"""

    def test_parent_can_only_access_own_child_data(self):
        """Parent should only access their own child's data"""
        tenant = Tenant.objects.create(name="Org", slug="org")
        parent1 = User.objects.create_user(
            username="parent1", password="pass", tenant=tenant, role="parent"
        )
        parent2 = User.objects.create_user(
            username="parent2", password="pass", tenant=tenant, role="parent"
        )
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")

        child1 = Child.objects.create(
            tenant=tenant,
            name="Child 1",
            parent_name="Parent 1",
            parent_user=parent1,
            classroom=classroom,
        )
        child2 = Child.objects.create(
            tenant=tenant,
            name="Child 2",
            parent_name="Parent 2",
            parent_user=parent2,
            classroom=classroom,
        )

        client = APIClient()
        client.force_authenticate(user=parent1)

        response = client.get("/api/children/")
        child_ids = [c["id"] for c in response.data["results"]]

        assert child1.id in child_ids
        assert child2.id not in child_ids

    def test_admin_can_bulk_update_attendance(self):
        """Admin should be able to bulk update attendance for all children"""
        tenant = Tenant.objects.create(name="Org", slug="org")
        admin = User.objects.create_user(
            username="admin", password="pass", tenant=tenant, role="admin"
        )
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")

        children = [
            Child.objects.create(
                tenant=tenant,
                name=f"Child {i}",
                parent_name=f"Parent {i}",
                classroom=classroom,
            )
            for i in range(3)
        ]

        client = APIClient()
        client.force_authenticate(user=admin)

        today = date.today()
        data = {
            "records": [
                {"child_id": child.id, "status": "present", "date": str(today)}
                for child in children
            ]
        }

        response = client.post("/api/attendance/bulk-update/", data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify all records created
        for child in children:
            att = AttendanceRecord.objects.filter(
                tenant=tenant, child=child, date=today
            ).first()
            assert att is not None
            assert att.status == "present"


@pytest.mark.django_db
class TestDataIntegrity:
    """Test data integrity constraints"""

    def test_duplicate_attendance_rejected(self):
        """Cannot create duplicate attendance for same child on same date"""
        from django.db import IntegrityError

        tenant = Tenant.objects.create(name="Org", slug="org")
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")
        child = Child.objects.create(
            tenant=tenant, name="Child", parent_name="Parent", classroom=classroom
        )

        today = date.today()
        AttendanceRecord.objects.create(
            tenant=tenant, child=child, date=today, status="present"
        )

        # Try to create duplicate
        with pytest.raises(IntegrityError):
            AttendanceRecord.objects.create(
                tenant=tenant, child=child, date=today, status="absent"
            )

    def test_future_attendance_rejected(self):
        """Cannot create attendance for future dates"""
        from django.core.exceptions import ValidationError

        tenant = Tenant.objects.create(name="Org", slug="org")
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")
        child = Child.objects.create(
            tenant=tenant, name="Child", parent_name="Parent", classroom=classroom
        )

        future_date = date.today() + timedelta(days=1)
        att = AttendanceRecord(
            tenant=tenant, child=child, date=future_date, status="present"
        )

        with pytest.raises(ValidationError):
            att.full_clean()


@pytest.mark.django_db
class TestQueryOptimization:
    """Test that queries are optimized and don't have N+1 issues"""

    def test_child_list_query_count(self, django_assert_num_queries):
        """ChildListCreateView should not have N+1 queries"""
        tenant = Tenant.objects.create(name="Org", slug="org")
        admin = User.objects.create_user(
            username="admin", password="pass", tenant=tenant, role="admin"
        )
        classroom = ClassRoom.objects.create(tenant=tenant, name="Class")

        # Create multiple children with clubs
        club1 = Club.objects.create(tenant=tenant, name="Club 1")
        club2 = Club.objects.create(tenant=tenant, name="Club 2")

        for i in range(10):
            child = Child.objects.create(
                tenant=tenant,
                name=f"Child {i}",
                parent_name=f"Parent {i}",
                classroom=classroom,
            )
            child.clubs.add(club1, club2)

        client = APIClient()
        client.force_authenticate(user=admin)

        # Should only make ~3 queries: children, classroom, clubs
        with django_assert_num_queries(3):
            response = client.get("/api/children/")
            assert len(response.data["results"]) == 10
