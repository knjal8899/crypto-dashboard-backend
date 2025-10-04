"""
Serializers for cryptocurrency data.
"""

from rest_framework import serializers
from .models import Cryptocurrency, PriceHistory, MarketData


class CryptocurrencySerializer(serializers.ModelSerializer):
    """Serializer for Cryptocurrency model."""
    
    class Meta:
        model = Cryptocurrency
        fields = [
            'id',
            'coin_id',
            'symbol',
            'name',
            'image_url',
            'current_price',
            'market_cap',
            'total_volume',
            'price_change_24h',
            'price_change_percentage_24h',
            'market_cap_rank',
            'last_updated',
            'created_at',
        ]
        read_only_fields = ['id', 'last_updated', 'created_at']


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for PriceHistory model."""
    
    cryptocurrency_name = serializers.CharField(
        source='cryptocurrency.name', 
        read_only=True
    )
    cryptocurrency_symbol = serializers.CharField(
        source='cryptocurrency.symbol', 
        read_only=True
    )
    
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'cryptocurrency',
            'cryptocurrency_name',
            'cryptocurrency_symbol',
            'price',
            'market_cap',
            'total_volume',
            'timestamp',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class MarketDataSerializer(serializers.ModelSerializer):
    """Serializer for MarketData model."""
    
    class Meta:
        model = MarketData
        fields = [
            'id',
            'total_market_cap',
            'total_volume',
            'active_cryptocurrencies',
            'market_cap_percentage_btc',
            'market_cap_percentage_eth',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']


class TopCoinsSerializer(serializers.Serializer):
    """Serializer for top N coins endpoint."""
    
    limit = serializers.IntegerField(
        min_value=1, 
        max_value=100, 
        default=10,
        help_text="Number of top coins to return"
    )
    sort_by = serializers.ChoiceField(
        choices=[
            ('market_cap_rank', 'Market Cap Rank'),
            ('market_cap', 'Market Cap'),
            ('price_change_percentage_24h', '24h Change %'),
            ('total_volume', 'Volume'),
        ],
        default='market_cap_rank',
        help_text="Field to sort by"
    )


class HistoricalDataSerializer(serializers.Serializer):
    """Serializer for historical data endpoint."""
    
    coin_id = serializers.CharField(
        help_text="CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')"
    )
    days = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=30,
        help_text="Number of days of historical data"
    )
