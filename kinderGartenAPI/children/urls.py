from django.urls import path
from .views_upload import UploadAvatarView
from .views import ChildDetailView, ChildListCreateView, ClassRoomListCreateView

urlpatterns = [
    path("classes/", ClassRoomListCreateView.as_view(), name="classroom-list-create"),
    path("", ChildListCreateView.as_view(), name="child-list-create"),
    path("upload-avatar/", UploadAvatarView.as_view(), name="upload-avatar"),
    path("<int:pk>/", ChildDetailView.as_view(), name="child-detail"),


]
