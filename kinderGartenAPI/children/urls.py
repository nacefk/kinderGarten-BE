from django.urls import path
from .views_upload import UploadAvatarView
from .views import ChildDetailView, ChildListCreateView, ClassRoomListCreateView, ClubListCreateView, ClubDetailView, MyChildView

urlpatterns = [
    path("classes/", ClassRoomListCreateView.as_view(), name="classroom-list-create"),
    path("", ChildListCreateView.as_view(), name="child-list-create"),
    path("upload-avatar/", UploadAvatarView.as_view(), name="upload-avatar"),
    path("<int:pk>/", ChildDetailView.as_view(), name="child-detail"),
    path("clubs/", ClubListCreateView.as_view(), name="club-list-create"),
    path("clubs/<int:pk>/", ClubDetailView.as_view(), name="club-detail"),
    path("me/", MyChildView.as_view(), name="my-child"),



]
