from django.urls import path
from .views import TopCoinsView, CoinHistoryView, MarketDataView, GainersLosersView, PriceHistoryView, CoinDetailView, WatchlistView

urlpatterns = [
    path("top", TopCoinsView.as_view(), name="coins-top"),
    path("<str:coin_id>/history", CoinHistoryView.as_view(), name="coin-history"),
    path("market-data", MarketDataView.as_view(), name="market-data"),
    path("gainers-losers", GainersLosersView.as_view(), name="gainers-losers"),
    path("<str:coin_id>/price-history", PriceHistoryView.as_view(), name="price-history"),
    path("<str:coin_id>/detail", CoinDetailView.as_view(), name="coin-detail"),
    path("watchlist", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/<str:coin_id>", WatchlistView.as_view(), name="watchlist-coin"),
]
