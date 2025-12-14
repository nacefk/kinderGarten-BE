from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_upload import UploadAvatarView
from .views import (
    ChildDetailView,
    ChildListCreateView,
    ClassRoomListCreateView,
    ClassRoomDetailView,
    ClubListCreateView,
    ClubDetailView,
    MyChildView,
)

# Create a router for ViewSet actions
router = DefaultRouter()

urlpatterns = [
    path("classes/", ClassRoomListCreateView.as_view(), name="classroom-list-create"),
    path("classes/<int:pk>/", ClassRoomDetailView.as_view(), name="classroom-detail"),
    path("", ChildListCreateView.as_view(), name="child-list-create"),
    path("upload-avatar/", UploadAvatarView.as_view(), name="upload-avatar"),
    path(
        "<int:pk>/",
        ChildDetailView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="child-detail",
    ),
    path(
        "<int:pk>/enable-mobile-app/",
        ChildDetailView.as_view({"post": "enable_mobile_app"}),
        name="child-enable-mobile-app",
    ),
    path(
        "<int:pk>/disable-mobile-app/",
        ChildDetailView.as_view({"post": "disable_mobile_app"}),
        name="child-disable-mobile-app",
    ),
    path("clubs/", ClubListCreateView.as_view(), name="club-list-create"),
    path("clubs/<int:pk>/", ClubDetailView.as_view(), name="club-detail"),
    path("me/", MyChildView.as_view(), name="my-child"),
]
