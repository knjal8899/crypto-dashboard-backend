import re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from coins.services import fetch_coin_market_by_id, fetch_coin_history


COIN_SYNONYMS = {
    'bitcoin': ['btc', 'bitcoin'],
    'ethereum': ['eth', 'ethereum'],
}


def normalize_coin(q: str) -> str | None:
    ql = q.lower()
    for cid, keys in COIN_SYNONYMS.items():
        for k in keys:
            if re.search(rf"\b{k}\b", ql):
                return cid
    # fallback: extract single word after 'of' or last token
    m = re.search(r"price of ([a-z0-9-]+)", ql)
    if m:
        return m.group(1)
    m = re.search(r"trend of ([a-z0-9-]+)", ql)
    if m:
        return m.group(1)
    parts = re.findall(r"[a-z0-9-]+", ql)
    return parts[-1] if parts else None


class QaQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        text = request.query_params.get('text', '')
        if not text:
            return Response({"detail": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

        ql = text.lower()
        coin_id = normalize_coin(ql)
        if not coin_id:
            return Response({"answer": "Sorry, I couldn't identify the coin."})

        if "price" in ql:
            data = fetch_coin_market_by_id(coin_id)
            if not data:
                return Response({"answer": f"No data for {coin_id}."})
            price = data.get("current_price")
            return Response({"answer": f"The price of {coin_id} is ${price}.", "coin": coin_id, "price_usd": price})

        # trend handling - check for N-day
        m = re.search(r"(\d+)[- ]?day", ql)
        days = int(m.group(1)) if m else 7
        hist = fetch_coin_history(coin_id, days=days)
        prices = hist.get("prices", [])
        return Response({"answer": f"Showing {days}-day trend for {coin_id}.", "coin": coin_id, "days": days, "prices": prices})

# Create your views here.
