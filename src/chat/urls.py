from django.urls import path
from .views import QaQueryView, SuggestionsView, ChatMessageView


urlpatterns = [
    path("query", QaQueryView.as_view(), name="qa-query"),
    path("suggestions", SuggestionsView.as_view(), name="qa-suggestions"),
    path("message", ChatMessageView.as_view(), name="chat-message"),
]


