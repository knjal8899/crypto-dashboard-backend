"""
URL configuration for chat app.
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    path('sessions/', views.chat_sessions_list, name='chat-sessions-list'),
    path('sessions/create/', views.create_chat_session, name='create-chat-session'),
    path('sessions/<str:session_id>/', views.ChatSessionView.as_view(), name='chat-session-detail'),
]
