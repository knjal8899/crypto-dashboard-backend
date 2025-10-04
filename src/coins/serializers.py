from rest_framework import serializers
from .models import Coin, PriceHistory


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ["id", "cg_id", "symbol", "name", "last_price_usd", "last_updated_at"]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["date", "price_usd"]
