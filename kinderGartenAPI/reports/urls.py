from django.urls import path
from .views import (
    DailyReportDetailView,
    DailyReportListCreateView,
    ReportMediaDeleteView,
)

urlpatterns = [
    path("", DailyReportListCreateView.as_view(), name="daily-report-list-create"),
    path("<int:pk>/", DailyReportDetailView.as_view(), name="daily-report-detail"),
    path(
        "media/<int:pk>/", ReportMediaDeleteView.as_view(), name="report-media-delete"
    ),
]
