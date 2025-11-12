from django.urls import path
from .views import (
    AttendanceSummaryView,
    AttendanceListView,
    AttendanceBulkUpdateView,
    ExtraHourPendingListView,
)

urlpatterns = [
    path("", AttendanceListView.as_view(), name="attendance-list"),
    path("summary/", AttendanceSummaryView.as_view(), name="attendance-summary"),
    path("update/", AttendanceBulkUpdateView.as_view(), name="attendance-update"),
    path("extra/", ExtraHourPendingListView.as_view(), name="extra-hour-pending"),
]
