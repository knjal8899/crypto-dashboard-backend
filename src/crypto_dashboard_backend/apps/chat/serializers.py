"""
Serializers for chat app.
"""

from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model."""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'message_type',
            'content',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model."""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id',
            'session_id',
            'created_at',
            'last_activity',
            'messages',
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request."""
    
    message = serializers.CharField(
        max_length=1000,
        help_text="User's message to the chat assistant"
    )
    session_id = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Optional session ID to maintain conversation context"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    
    response = serializers.CharField(
        help_text="Assistant's response to the user's message"
    )
    session_id = serializers.CharField(
        help_text="Session ID for maintaining conversation context"
    )
    message_type = serializers.CharField(
        help_text="Type of message (user/assistant)"
    )
    timestamp = serializers.DateTimeField(
        help_text="Timestamp of the response"
    )
