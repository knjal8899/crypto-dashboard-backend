from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Coin, PriceHistory
from .serializers import CoinSerializer, PriceHistorySerializer


@api_view(["GET"])
def top_coins(request):
    try:
        limit = int(request.query_params.get("limit", "10"))
    except ValueError:
        limit = 10
    qs = Coin.objects.all().order_by(F("volume_24h_usd").desc(nulls_last=True))[:limit]
    return Response(CoinSerializer(qs, many=True).data)


@api_view(["GET"])
def coin_history(request, coin_id: int):
    try:
        limit = int(request.query_params.get("limit", "200"))
    except ValueError:
        limit = 200
    try:
        coin = Coin.objects.get(pk=coin_id)
    except Coin.DoesNotExist:
        return Response({"detail": "Coin not found"}, status=status.HTTP_404_NOT_FOUND)
    qs = (
        PriceHistory.objects.filter(coin=coin)
        .order_by("timestamp")
        .all()[:limit]
    )
    return Response({
        "coin": CoinSerializer(coin).data,
        "prices": PriceHistorySerializer(qs, many=True).data,
    })


# Create your views here.
