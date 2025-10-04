"""
Admin configuration for crypto app.
"""

from django.contrib import admin
from .models import Cryptocurrency, PriceHistory, MarketData


@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    """Admin interface for Cryptocurrency model."""
    
    list_display = [
        'name',
        'symbol',
        'coin_id',
        'current_price',
        'market_cap_rank',
        'price_change_percentage_24h',
        'last_updated',
    ]
    list_filter = [
        'market_cap_rank',
        'last_updated',
        'created_at',
    ]
    search_fields = [
        'name',
        'symbol',
        'coin_id',
    ]
    readonly_fields = [
        'last_updated',
        'created_at',
    ]
    ordering = ['market_cap_rank']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    """Admin interface for PriceHistory model."""
    
    list_display = [
        'cryptocurrency',
        'price',
        'timestamp',
        'created_at',
    ]
    list_filter = [
        'cryptocurrency',
        'timestamp',
        'created_at',
    ]
    search_fields = [
        'cryptocurrency__name',
        'cryptocurrency__symbol',
    ]
    readonly_fields = [
        'created_at',
    ]
    ordering = ['-timestamp']


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    """Admin interface for MarketData model."""
    
    list_display = [
        'total_market_cap',
        'total_volume',
        'active_cryptocurrencies',
        'market_cap_percentage_btc',
        'market_cap_percentage_eth',
        'timestamp',
    ]
    readonly_fields = [
        'timestamp',
    ]
    ordering = ['-timestamp']
