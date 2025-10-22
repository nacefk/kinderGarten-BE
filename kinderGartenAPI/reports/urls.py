from django.urls import path
from .views import DailyReportListCreateView

urlpatterns = [
    path("", DailyReportListCreateView.as_view(), name="daily-report-list-create"),
]
