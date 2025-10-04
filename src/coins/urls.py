from django.urls import path
from .views import TopCoinsView, CoinHistoryView

urlpatterns = [
    path("top", TopCoinsView.as_view(), name="coins-top"),
    path("<str:coin_id>/history", CoinHistoryView.as_view(), name="coin-history"),
]
