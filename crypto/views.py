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


def _normalize_text(text: str) -> str:
    return text.strip().lower()


@api_view(["POST"])
def qa(request):
    """Rule-based Q&A for simple queries.

    Examples:
    - "what is the price of bitcoin"
    - "show me the 7-day trend of ethereum"
    """
    query: str = str(request.data.get("query", ""))
    if not query:
        return Response({"answer": "Please provide a query."}, status=status.HTTP_400_BAD_REQUEST)

    q = _normalize_text(query)

    # price question
    if "price" in q:
        # attempt to match coin by name or symbol in our DB
        for coin in Coin.objects.all():
            if coin.name.lower() in q or coin.symbol.lower() in q or coin.coingecko_id.lower() in q:
                if coin.price_usd is None:
                    return Response({"answer": f"I don't have a current price for {coin.name} yet."})
                return Response({
                    "answer": f"The price of {coin.name} ({coin.symbol.upper()}) is ${coin.price_usd}.",
                    "coin": CoinSerializer(coin).data,
                })

    # trend question - look for N-day or default 7-day trend
    if "trend" in q or "chart" in q or "history" in q:
        days = 7
        # naive days extraction
        for token in q.split():
            if token.endswith("-day") and token[:-4].isdigit():
                days = int(token[:-4])
            if token.endswith("day") and token[:-3].isdigit():
                days = int(token[:-3])

        for coin in Coin.objects.all():
            if coin.name.lower() in q or coin.symbol.lower() in q or coin.coingecko_id.lower() in q:
                qs = (
                    PriceHistory.objects.filter(coin=coin)
                    .order_by("-timestamp")
                    .all()[: days * 2]
                )
                return Response({
                    "answer": f"Here is the {days}-day trend for {coin.name}.",
                    "coin": CoinSerializer(coin).data,
                    "prices": PriceHistorySerializer(qs, many=True).data,
                })

    return Response({"answer": "Sorry, I didn't understand. Try 'price of bitcoin' or '7-day trend of ethereum'."})


# Create your views here.
