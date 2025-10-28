from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, WeeklyPlanViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"plans", WeeklyPlanViewSet, basename="weeklyplan")

urlpatterns = [
    path("", include(router.urls)),
]
