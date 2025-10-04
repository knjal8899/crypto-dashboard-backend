"""
URL configuration for crypto app.
"""

from django.urls import path
from . import views

app_name = 'crypto'

urlpatterns = [
    path('top-coins/', views.TopCoinsView.as_view(), name='top-coins'),
    path('historical/', views.HistoricalDataView.as_view(), name='historical-data'),
    path('coin/<str:coin_id>/', views.CoinDetailView.as_view(), name='coin-detail'),
    path('market-data/', views.MarketDataView.as_view(), name='market-data'),
    path('search/', views.search_coins, name='search-coins'),
    path('refresh/', views.refresh_data, name='refresh-data'),
]
