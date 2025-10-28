from rest_framework import generics, permissions
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # admin
            return Conversation.objects.all()
        return Conversation.objects.filter(parent=user)


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        serializer.save(sender=self.request.user, conversation_id=conversation_id)
