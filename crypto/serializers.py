from rest_framework import serializers

from .models import Coin, PriceHistory


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = [
            "id",
            "coingecko_id",
            "symbol",
            "name",
            "price_usd",
            "volume_24h_usd",
            "percent_change_24h",
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["timestamp", "price_usd"]


