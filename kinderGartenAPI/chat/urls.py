from django.urls import path
from .views import ConversationListView, ConversationDetailView, MessageCreateView

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('messages/', MessageCreateView.as_view(), name='message-create'),
]
