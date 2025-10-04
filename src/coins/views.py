from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Coin, PriceHistory
from .serializers import CoinSerializer, PriceHistorySerializer
from .services import fetch_top_coins, fetch_coin_history


class TopCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        market = fetch_top_coins(limit=limit)
        coins: List[Coin] = []
        with transaction.atomic():
            for item in market:
                coin, _ = Coin.objects.update_or_create(
                    cg_id=item["id"],
                    defaults={
                        "symbol": item.get("symbol", "").upper(),
                        "name": item.get("name", ""),
                        "last_price_usd": Decimal(str(item.get("current_price", 0))) if item.get("current_price") is not None else None,
                        "last_updated_at": datetime.now(timezone.utc),
                    },
                )
                coins.append(coin)
        return Response(CoinSerializer(coins, many=True).data)


class CoinHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, coin_id: str):
        try:
            days = int(request.query_params.get("days", 30))
        except (TypeError, ValueError):
            days = 30
        data = fetch_coin_history(coin_id, days=days)
        prices = data.get("prices", [])
        coin = Coin.objects.filter(cg_id=coin_id).first()
        if not coin:
            coin = Coin.objects.create(cg_id=coin_id, symbol=coin_id[:10].upper(), name=coin_id)
        history_objs: List[PriceHistory] = []
        with transaction.atomic():
            for ts, price in prices:
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                ph, _ = PriceHistory.objects.update_or_create(
                    coin=coin,
                    date=dt.date(),
                    defaults={"price_usd": Decimal(str(price))},
                )
                history_objs.append(ph)
        return Response(PriceHistorySerializer(history_objs, many=True).data)
