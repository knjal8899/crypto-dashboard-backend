from django.urls import path
from .views import QaQueryView


urlpatterns = [
    path("query", QaQueryView.as_view(), name="qa-query"),
]


