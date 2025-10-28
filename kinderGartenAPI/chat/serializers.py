from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'text', 'timestamp', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.username', read_only=True)
    admin_name = serializers.CharField(source='admin.username', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'parent', 'parent_name', 'admin', 'admin_name', 'messages']
