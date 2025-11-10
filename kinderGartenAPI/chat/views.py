from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


# ✅ GET (list) + POST (create or get) parent↔admin conversation
class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Conversation.objects.all()
        return Conversation.objects.filter(parent=user)

    def post(self, request, *args, **kwargs):
        """When a parent opens chat, create or get conversation with first admin"""
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            return Response({"error": "No admin found"}, status=status.HTTP_400_BAD_REQUEST)

        conversation, _ = Conversation.objects.get_or_create(
            parent=request.user,
            admin=admin_user,
        )
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Retrieve one conversation + its messages
class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated]


# ✅ Create new message in an existing conversation
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation")
        conversation = get_object_or_404(Conversation, id=conversation_id)

        user = self.request.user
        if user != conversation.parent and user != conversation.admin:
            raise PermissionDenied("You are not part of this conversation.")

        serializer.save(sender=user, conversation=conversation)
