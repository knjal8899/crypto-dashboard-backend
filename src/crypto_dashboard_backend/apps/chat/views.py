"""
Views for chat assistant endpoints.
"""

import uuid
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
)
from .services import ChatAssistantService


class ChatView(APIView):
    """API view for chat assistant."""
    
    def post(self, request):
        """Process a chat message and return a response."""
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'last_activity': timezone.now()}
        )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Process message and generate response
        chat_service = ChatAssistantService()
        response_data = chat_service.process_message(message, session_id)
        
        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=response_data['response']
        )
        
        # Update session activity
        session.last_activity = timezone.now()
        session.save()
        
        return Response(response_data, status=status.HTTP_200_OK)


class ChatSessionView(APIView):
    """API view for managing chat sessions."""
    
    def get(self, request, session_id):
        """Get chat session with all messages."""
        try:
            session = ChatSession.objects.get(session_id=session_id)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Chat session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, session_id):
        """Delete a chat session."""
        try:
            session = ChatSession.objects.get(session_id=session_id)
            session.delete()
            return Response(
                {'message': 'Chat session deleted successfully'},
                status=status.HTTP_200_OK
            )
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Chat session not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def chat_sessions_list(request):
    """List all chat sessions."""
    sessions = ChatSession.objects.all()[:50]  # Limit to 50 most recent
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_chat_session(request):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    session = ChatSession.objects.create(session_id=session_id)
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
