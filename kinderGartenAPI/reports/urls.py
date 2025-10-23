from django.urls import path
from .views import DailyReportDetailView, DailyReportListCreateView

urlpatterns = [
    path("", DailyReportListCreateView.as_view(), name="daily-report-list-create"),
    path("<int:pk>/", DailyReportDetailView.as_view(), name="daily-report-detail"),  # ✅ new

]
