from rest_framework import serializers
from .models import Coin, PriceHistory, Watchlist


class CoinSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='cg_id', read_only=True)
    marketCapRank = serializers.IntegerField(source='market_cap_rank', read_only=True)
    image = serializers.URLField(source='image_url', read_only=True)
    currentPrice = serializers.DecimalField(source='last_price_usd', max_digits=20, decimal_places=8, read_only=True)
    priceChangePercentage24h = serializers.DecimalField(source='last_pct_change_24h', max_digits=10, decimal_places=4, read_only=True)
    marketCap = serializers.DecimalField(source='market_cap_usd', max_digits=24, decimal_places=2, read_only=True)
    totalVolume = serializers.DecimalField(source='last_volume_24h_usd', max_digits=24, decimal_places=2, read_only=True)
    
    class Meta:
        model = Coin
        fields = [
            "id",
            "marketCapRank", 
            "image",
            "name",
            "symbol",
            "currentPrice",
            "priceChangePercentage24h",
            "marketCap",
            "totalVolume",
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["date", "price_usd"]


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ["coin", "added_at"]
