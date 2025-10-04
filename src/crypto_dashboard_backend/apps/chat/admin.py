"""
Admin configuration for chat app.
"""

from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for ChatSession model."""
    
    list_display = [
        'session_id',
        'created_at',
        'last_activity',
        'message_count',
    ]
    list_filter = [
        'created_at',
        'last_activity',
    ]
    search_fields = [
        'session_id',
    ]
    readonly_fields = [
        'created_at',
        'last_activity',
    ]
    ordering = ['-last_activity']
    
    def message_count(self, obj):
        """Display the number of messages in the session."""
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""
    
    list_display = [
        'session',
        'message_type',
        'content_preview',
        'timestamp',
    ]
    list_filter = [
        'message_type',
        'timestamp',
        'session',
    ]
    search_fields = [
        'content',
        'session__session_id',
    ]
    readonly_fields = [
        'timestamp',
    ]
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        """Display a preview of the message content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
