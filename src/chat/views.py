import re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

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

    @extend_schema(
        summary="Chat with crypto assistant",
        description="Ask questions about cryptocurrencies and get AI-powered responses with current data",
        parameters=[
            {
                'name': 'text',
                'type': 'string',
                'location': 'query',
                'description': 'Your question about cryptocurrencies',
                'required': True
            }
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'response': {'type': 'string'},
                    'coin_data': {'type': 'object', 'nullable': True},
                    'price_history': {'type': 'array', 'nullable': True}
                }
            },
            400: "Bad Request - Missing or invalid text parameter",
            401: "Unauthorized - Invalid or missing token"
        },
        tags=["Chat Assistant"]
    )
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

class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Autocomplete suggestions",
        description="Return simple suggestions for coin-related queries.",
        tags=["Chat Assistant"],
    )
    def get(self, request):
        return Response({
            "suggestions": [
                "Price of Bitcoin",
                "24h change of Ethereum",
                "Show top coins",
                "BTC last week trend",
            ]
        })


class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send message to chat assistant",
        description="Send a message to the chat assistant and get a response.",
        request={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "sessionId": {"type": "string", "nullable": True}
            },
            "required": ["message"]
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "reply": {"type": "string"}
                }
            },
            400: "Bad Request - Missing message"
        },
        tags=["Chat Assistant"],
    )
    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response({"detail": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Simple rule-based responses for now
        message_lower = message.lower()
        
        if "bitcoin" in message_lower or "btc" in message_lower:
            if "price" in message_lower:
                return Response({"reply": "The current price of Bitcoin is $112,614.00."})
            elif "change" in message_lower or "24h" in message_lower:
                return Response({"reply": "Bitcoin's 24h change is +2.51%."})
            else:
                return Response({"reply": "Bitcoin (BTC) is the world's first cryptocurrency. It's currently trading at $112,614.00 with a 24h change of +2.51%."})
        
        elif "ethereum" in message_lower or "eth" in message_lower:
            if "price" in message_lower:
                return Response({"reply": "The current price of Ethereum is $3,200.00."})
            elif "change" in message_lower or "24h" in message_lower:
                return Response({"reply": "Ethereum's 24h change is -1.2%."})
            else:
                return Response({"reply": "Ethereum (ETH) is a decentralized platform that runs smart contracts. It's currently trading at $3,200.00 with a 24h change of -1.2%."})
        
        elif "top" in message_lower and "coin" in message_lower:
            return Response({"reply": "The top cryptocurrencies by market cap are: 1. Bitcoin (BTC) - $112,614.00, 2. Ethereum (ETH) - $3,200.00, 3. BNB (BNB) - $350.00."})
        
        elif "market" in message_lower:
            return Response({"reply": "The total cryptocurrency market cap is $2.54 trillion with Bitcoin dominance at 45.67%. The market is up 2.51% in the last 24 hours."})
        
        else:
            return Response({"reply": "I can help you with cryptocurrency information. Try asking about Bitcoin, Ethereum, top coins, or market data."})

# Create your views here.
