"""
Performance and load testing script using Locust
Tests response times, throughput, and identifies bottlenecks

Usage:
    locust -f load_tests.py --host http://localhost:8000

Or run with custom settings:
    locust -f load_tests.py --host http://localhost:8000 -u 100 -r 10 --run-time 5m
"""

from locust import HttpUser, task, between
import random
import json


class ChildrenAPIUser(HttpUser):
    """Simulates a user interacting with Children API"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Authenticate before making requests"""
        # In real scenario, get auth token
        self.token = "your-auth-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        self.child_id = None
        self.classroom_id = None

    @task(3)
    def list_children(self):
        """List children - should be optimized for performance"""
        with self.client.get(
            "/api/children/", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                # Extract first child ID for detail view
                data = response.json()
                if data["results"]:
                    self.child_id = data["results"][0]["id"]
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_child_detail(self):
        """Get child detail - tests select_related optimization"""
        if self.child_id:
            with self.client.get(
                f"/api/children/{self.child_id}/",
                headers=self.headers,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Got status code {response.status_code}")

    @task(1)
    def create_child(self):
        """Create new child - tests write performance"""
        payload = {
            "name": f"Test Child {random.randint(1000, 9999)}",
            "parent_name": "Test Parent",
            "classroom": self.classroom_id,
            "has_mobile_app": True,
        }

        with self.client.post(
            "/api/children/",
            data=json.dumps(payload),
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class AttendanceAPIUser(HttpUser):
    """Simulates a user tracking attendance"""

    wait_time = between(1, 2)

    def on_start(self):
        """Authenticate and get class info"""
        self.token = "your-auth-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(2)
    def list_attendance(self):
        """List attendance records"""
        with self.client.get(
            "/api/attendance/records/", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(3)
    def bulk_update_attendance(self):
        """Bulk update attendance - critical operation"""
        payload = {
            "records": [
                {
                    "child_id": random.randint(1, 50),
                    "status": random.choice(["present", "absent"]),
                    "date": "2024-01-15",
                }
                for _ in range(20)
            ]
        }

        with self.client.post(
            "/api/attendance/bulk-update/",
            data=json.dumps(payload),
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class ReportsAPIUser(HttpUser):
    """Simulates a user creating and reading reports"""

    wait_time = between(2, 5)

    def on_start(self):
        self.token = "your-auth-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(1)
    def list_reports(self):
        """List daily reports"""
        with self.client.get(
            "/api/reports/", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def create_report(self):
        """Create daily report - tests file upload and write performance"""
        payload = {
            "child": random.randint(1, 50),
            "report_text": f"Daily report {random.randint(1000, 9999)}",
            "mood": random.choice(["happy", "neutral", "sad"]),
        }

        with self.client.post(
            "/api/reports/",
            data=json.dumps(payload),
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class ChatAPIUser(HttpUser):
    """Simulates chat interactions"""

    wait_time = between(1, 3)

    def on_start(self):
        self.token = "your-auth-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(2)
    def list_conversations(self):
        """List conversations - tests tenant filtering"""
        with self.client.get(
            "/api/chat/conversations/", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def send_message(self):
        """Send a message"""
        payload = {
            "conversation_id": random.randint(1, 20),
            "text": f"Message {random.randint(1000, 9999)}",
        }

        with self.client.post(
            "/api/chat/messages/",
            data=json.dumps(payload),
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


# Performance targets (tune these based on requirements)
PERFORMANCE_TARGETS = {
    "list_children": {
        "p50": 200,  # 50th percentile: 200ms
        "p95": 500,  # 95th percentile: 500ms
        "p99": 1000,  # 99th percentile: 1000ms
    },
    "get_child_detail": {
        "p50": 150,
        "p95": 400,
        "p99": 800,
    },
    "bulk_update_attendance": {
        "p50": 300,
        "p95": 700,
        "p99": 1500,
    },
    "list_reports": {
        "p50": 250,
        "p95": 600,
        "p99": 1200,
    },
}


if __name__ == "__main__":
    # Run with: locust -f load_tests.py --host http://localhost:8000
    # or: locust -f load_tests.py --host http://localhost:8000 -u 100 -r 10 --run-time 5m
    pass
