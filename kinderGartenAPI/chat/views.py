from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
import logging

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.permissions import IsTenantMember

User = get_user_model()
logger = logging.getLogger("api")


# ✅ GET (list) + POST (create or get) parent↔admin conversation
class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """✅ TENANT-SAFE: Filter by tenant and user role"""
        user = self.request.user
        tenant = user.tenant

        if user.role == "admin":
            return Conversation.objects.filter(tenant=tenant).select_related(
                "parent", "admin"
            )
        else:
            return Conversation.objects.filter(
                tenant=tenant, parent=user
            ).select_related("parent", "admin")

    def post(self, request, *args, **kwargs):
        """When a parent opens chat, create or get conversation with first admin"""
        tenant = request.user.tenant

        admin_user = User.objects.filter(tenant=tenant, role="admin").first()

        if not admin_user:
            logger.warning(f"No admin found in tenant {tenant.slug}")
            return Response(
                {"error": "No admin found in your organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation, _ = Conversation.objects.get_or_create(
            tenant=tenant,
            parent=request.user,
            admin=admin_user,
        )
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ Retrieve one conversation + its messages
class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

    def get_queryset(self):
        """✅ OPTIMIZED: select_related for user optimization"""
        return (
            Conversation.objects.filter(tenant=self.request.user.tenant)
            .select_related("parent", "admin")
            .prefetch_related("messages")  # ✅ Messages optimization
        )


# ✅ Create new message in an existing conversation
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """✅ SECURE: Verify user is part of conversation"""
        conversation_id = self.request.data.get("conversation")
        conversation = get_object_or_404(
            Conversation, id=conversation_id, tenant=self.request.user.tenant
        )

        user = self.request.user
        if user != conversation.parent and user != conversation.admin:
            logger.warning(
                f"Unauthorized message attempt by {user.username} "
                f"in conversation {conversation_id}"
            )
            raise PermissionDenied("You are not part of this conversation.")

        serializer.save(
            sender=user, conversation=conversation, tenant=self.request.user.tenant
        )
