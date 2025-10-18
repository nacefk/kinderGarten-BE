from django.urls import path
from .views import ChildListCreateView, ClassRoomListCreateView

urlpatterns = [
    path("classes/", ClassRoomListCreateView.as_view(), name="classroom-list-create"),
    path("", ChildListCreateView.as_view(), name="child-list-create"),
]
