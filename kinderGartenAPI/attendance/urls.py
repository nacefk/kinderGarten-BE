from django.urls import path
from .views import (
    AttendanceSummaryView,
    AttendanceListView,
    AttendanceBulkUpdateView,
    ExtraHourApproveRejectView,
    ExtraHourCreateView,
    ExtraHourPendingListView,
    ExtraHourRequestCreateView,
)

urlpatterns = [
    path("", AttendanceListView.as_view(), name="attendance-list"),
    path("summary/", AttendanceSummaryView.as_view(), name="attendance-summary"),
    path("update/", AttendanceBulkUpdateView.as_view(), name="attendance-update"),
    path("extra/", ExtraHourPendingListView.as_view(), name="extra-hour-pending"),
    path("extra-hours/", ExtraHourCreateView.as_view(), name="extra-hour-create"),
    path(
        "extra/<int:pk>/action/",
        ExtraHourApproveRejectView.as_view(),
        name="extra-hour-action",
    ),
    path(
        "extra/request/",
        ExtraHourRequestCreateView.as_view(),
        name="extra-hour-request",
    ),
]
