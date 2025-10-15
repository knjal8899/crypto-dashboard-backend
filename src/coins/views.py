from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Coin, PriceHistory, Watchlist
from .serializers import CoinSerializer, PriceHistorySerializer
from .services import fetch_top_coins, fetch_coin_history, fetch_global_market_data, fetch_coin_detailed_info, fetch_coin_chart_data


class TopCoinsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get top cryptocurrencies",
        description="Fetch the top cryptocurrencies by market cap from CoinGecko API",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of coins to return (default: 10)',
                default=10
            )
        ],
        responses={
            200: CoinSerializer(many=True),
            401: "Unauthorized - Invalid or missing token"
        },
        tags=["Cryptocurrencies"]
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        market = fetch_top_coins(limit=limit)
        # Upsert latest snapshot, then serve a paginated queryset from the DB
        with transaction.atomic():
            for item in market:
                Coin.objects.update_or_create(
                    cg_id=item["id"],
                    defaults={
                        "symbol": item.get("symbol", "").upper(),
                        "name": item.get("name", ""),
                        "last_price_usd": Decimal(str(item.get("current_price", 0))) if item.get("current_price") is not None else None,
                        "last_volume_24h_usd": Decimal(str(item.get("total_volume", 0))) if item.get("total_volume") is not None else None,
                        "last_pct_change_24h": Decimal(str(item.get("price_change_percentage_24h", 0))) if item.get("price_change_percentage_24h") is not None else None,
                        "market_cap_rank": item.get("market_cap_rank"),
                        "market_cap_usd": Decimal(str(item.get("market_cap", 0))) if item.get("market_cap") is not None else None,
                        "image_url": item.get("image"),
                        "last_updated_at": datetime.now(timezone.utc),
                    },
                )

        # Queryset with ordering; prefetch related collections if needed later
        queryset = (
            Coin.objects.all()
            .order_by("market_cap_rank", "name")
        )

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = CoinSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class CoinHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get coin price history (legacy endpoint)",
        description="Get historical price data for a specific coin. This endpoint stores data in database and returns PriceHistory objects.",
        parameters=[
            OpenApiParameter(
                name="days",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of days of history to fetch (default: 30)",
                default=30
            )
        ],
        responses={
            200: PriceHistorySerializer(many=True),
            401: "Unauthorized - Invalid or missing token"
        },
        tags=["Cryptocurrencies"],
    )
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
        with transaction.atomic():
            for ts, price in prices:
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                PriceHistory.objects.update_or_create(
                    coin=coin,
                    date=dt.date(),
                    defaults={"price_usd": Decimal(str(price))},
                )

        # Serve paginated history from DB with efficient relation loading
        history_qs = (
            PriceHistory.objects.select_related("coin")
            .filter(coin=coin)
            .order_by("date")
        )
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(history_qs, request, view=self)
        data = PriceHistorySerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class MarketDataView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Global market data",
        description="Return global cryptocurrency market data including Bitcoin dominance.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "totalMarketCap": {"type": "number"},
                    "totalVolume": {"type": "number"},
                    "marketCapChangePercentage24h": {"type": "number"},
                    "activeCoins": {"type": "number"},
                    "bitcoinDominance": {"type": "number"}
                }
            }
        },
        tags=["Cryptocurrencies"],
    )
    def get(self, request):
        global_data = fetch_global_market_data()
        data = global_data.get("data", {})
        
        return Response({
            "totalMarketCap": data.get("total_market_cap", {}).get("usd", 0),
            "totalVolume": data.get("total_volume", {}).get("usd", 0),
            "marketCapChangePercentage24h": data.get("market_cap_change_percentage_24h_usd", 0),
            "activeCoins": data.get("active_cryptocurrencies", 0),
            "bitcoinDominance": data.get("market_cap_percentage", {}).get("btc", 0)
        }, status=status.HTTP_200_OK)


class GainersLosersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Top gainers and losers",
        description="Compute top gainers and losers over 24h from the current market snapshot.",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of gainers/losers to include per side (default 5)",
                default=5,
            )
        ],
        tags=["Cryptocurrencies"],
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5

        market = fetch_top_coins(limit=100)

        def pct(item):
            val = item.get("price_change_percentage_24h")
            try:
                return float(val) if val is not None else 0.0
            except (TypeError, ValueError):
                return 0.0

        sorted_by_change = sorted(market, key=pct, reverse=True)
        gainers = sorted_by_change[:limit]
        losers = list(reversed(sorted_by_change))[:limit]

        return Response({
            "gainers": [
                {
                    "id": c.get("id"),
                    "symbol": c.get("symbol"),
                    "name": c.get("name"),
                    "image": c.get("image"),
                    "priceChangePercentage24h": c.get("price_change_percentage_24h"),
                }
                for c in gainers
            ],
            "losers": [
                {
                    "id": c.get("id"),
                    "symbol": c.get("symbol"),
                    "name": c.get("name"),
                    "image": c.get("image"),
                    "priceChangePercentage24h": c.get("price_change_percentage_24h"),
                }
                for c in losers
            ],
        }, status=status.HTTP_200_OK)


class PriceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get comprehensive chart data for coin",
        description="Get price history, volume, and market cap data for a specific coin for charting purposes.",
        parameters=[
            OpenApiParameter(
                name="range",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Time range: 1d, 7d, 30d, 90d, 1y (default: 7d)",
                default="7d"
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "prices": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    },
                    "volumes": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    },
                    "marketCaps": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    }
                }
            }
        },
        tags=["Cryptocurrencies"],
    )
    def get(self, request, coin_id: str):
        range_param = request.query_params.get("range", "7d")
        
        # Map frontend range to CoinGecko days
        range_mapping = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        days = range_mapping.get(range_param, 7)
        
        # Fetch comprehensive chart data
        chart_data = fetch_coin_chart_data(coin_id, days=days)
        
        return Response({
            "prices": chart_data.get("prices", []),
            "volumes": chart_data.get("total_volumes", []),
            "marketCaps": chart_data.get("market_caps", [])
        }, status=status.HTTP_200_OK)


class CoinDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get detailed coin information",
        description="Get comprehensive information about a specific coin including current price, market data, and statistics.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "symbol": {"type": "string"},
                    "image": {"type": "string"},
                    "currentPrice": {"type": "number"},
                    "marketCap": {"type": "number"},
                    "totalVolume": {"type": "number"},
                    "priceChange24h": {"type": "number"},
                    "priceChange7d": {"type": "number"},
                    "priceChange30d": {"type": "number"},
                    "marketCapRank": {"type": "number"},
                    "circulatingSupply": {"type": "number"},
                    "totalSupply": {"type": "number"},
                    "maxSupply": {"type": "number"},
                    "ath": {"type": "number"},
                    "atl": {"type": "number"}
                }
            }
        },
        tags=["Cryptocurrencies"],
    )
    def get(self, request, coin_id: str):
        coin_data = fetch_coin_detailed_info(coin_id)
        market_data = coin_data.get("market_data", {})
        
        return Response({
            "id": coin_data.get("id", coin_id),
            "name": coin_data.get("name", coin_id.title()),
            "symbol": coin_data.get("symbol", coin_id[:4].upper()),
            "image": coin_data.get("image", {}).get("large", ""),
            "currentPrice": market_data.get("current_price", {}).get("usd", 0),
            "marketCap": market_data.get("market_cap", {}).get("usd", 0),
            "totalVolume": market_data.get("total_volume", {}).get("usd", 0),
            "priceChange24h": market_data.get("price_change_percentage_24h", 0),
            "priceChange7d": market_data.get("price_change_percentage_7d", 0),
            "priceChange30d": market_data.get("price_change_percentage_30d", 0),
            "marketCapRank": market_data.get("market_cap_rank", 0),
            "circulatingSupply": market_data.get("circulating_supply", 0),
            "totalSupply": market_data.get("total_supply", 0),
            "maxSupply": market_data.get("max_supply", 0),
            "ath": market_data.get("ath", {}).get("usd", 0),
            "atl": market_data.get("atl", {}).get("usd", 0)
        }, status=status.HTTP_200_OK)


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user watchlist",
        description="Get the list of coins in the user's watchlist with full coin details.",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "symbol": {"type": "string"},
                        "image": {"type": "string"},
                        "currentPrice": {"type": "number"},
                        "priceChange24h": {"type": "number"},
                        "marketCap": {"type": "number"},
                        "addedAt": {"type": "string", "format": "date-time"}
                    }
                }
            }
        },
        tags=["Watchlist"],
    )
    def get(self, request):
        watchlist_items = Watchlist.objects.filter(user=request.user).select_related('coin').order_by('-added_at')
        
        watchlist_data = []
        for item in watchlist_items:
            coin = item.coin
            watchlist_data.append({
                "id": coin.cg_id,
                "name": coin.name,
                "symbol": coin.symbol,
                "image": coin.image_url or "",
                "currentPrice": float(coin.last_price_usd) if coin.last_price_usd else 0,
                "priceChange24h": float(coin.last_pct_change_24h) if coin.last_pct_change_24h else 0,
                "marketCap": float(coin.market_cap_usd) if coin.market_cap_usd else 0,
                "addedAt": item.added_at.isoformat()
            })
        
        return Response(watchlist_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add coin to watchlist",
        description="Add a coin to the user's watchlist. Can use URL path or request body.",
        request={
            "type": "object",
            "properties": {
                "coinId": {"type": "string"}
            }
        },
        responses={
            201: {"message": "Coin added to watchlist successfully"},
            400: "Bad Request - Coin already in watchlist or invalid coin ID"
        },
        tags=["Watchlist"],
    )
    def post(self, request, coin_id: str = None):
        # Support both URL path and request body
        if not coin_id:
            coin_id = request.data.get('coinId')
        
        if not coin_id or coin_id == 'undefined':
            return Response({"error": "Coin ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        coin, created = Coin.objects.get_or_create(
            cg_id=coin_id,
            defaults={
                "symbol": coin_id[:10].upper(),
                "name": coin_id.title()
            }
        )
        
        watchlist_item, created = Watchlist.objects.get_or_create(
            user=request.user,
            coin=coin
        )
        
        if created:
            return Response({"message": "Coin added to watchlist successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Coin already in watchlist"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Remove coin from watchlist",
        description="Remove a coin from the user's watchlist. Can use URL path or request body.",
        request={
            "type": "object",
            "properties": {
                "coinId": {"type": "string"}
            }
        },
        responses={
            200: {"message": "Coin removed from watchlist successfully"},
            404: "Not Found - Coin not in watchlist"
        },
        tags=["Watchlist"],
    )
    def delete(self, request, coin_id: str = None):
        # Support both URL path and request body
        if not coin_id:
            coin_id = request.data.get('coinId')
        
        if not coin_id or coin_id == 'undefined':
            return Response({"error": "Coin ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coin = Coin.objects.get(cg_id=coin_id)
            watchlist_item = Watchlist.objects.get(user=request.user, coin=coin)
            watchlist_item.delete()
            return Response({"message": "Coin removed from watchlist successfully"}, status=status.HTTP_200_OK)
        except (Coin.DoesNotExist, Watchlist.DoesNotExist):
            return Response({"error": "Coin not found in watchlist"}, status=status.HTTP_404_NOT_FOUND)
