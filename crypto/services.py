from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


@dataclass
class CoinMarket:
    id: str
    symbol: str
    name: str
    current_price: float
    total_volume: float
    price_change_percentage_24h: float | None


def fetch_top_coins_market_data(vs_currency: str = "usd", per_page: int = 10) -> list[CoinMarket]:
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h",
    }
    headers = {}
    api_key = None  # demo key optional; set via environment if needed
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data: list[dict[str, Any]] = resp.json()
    markets: list[CoinMarket] = []
    for item in data:
        markets.append(
            CoinMarket(
                id=item["id"],
                symbol=item["symbol"],
                name=item["name"],
                current_price=float(item.get("current_price") or 0.0),
                total_volume=float(item.get("total_volume") or 0.0),
                price_change_percentage_24h=(
                    float(item.get("price_change_percentage_24h"))
                    if item.get("price_change_percentage_24h") is not None
                    else None
                ),
            )
        )
    return markets


def fetch_coin_market_chart(coin_id: str, vs_currency: str = "usd", days: int = 30) -> list[tuple[datetime, float]]:
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "daily",
    }
    headers = {}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()
    prices: list[list[float]] = data.get("prices", [])
    result: list[tuple[datetime, float]] = []
    for ts_ms, price in prices:
        result.append((datetime.utcfromtimestamp(ts_ms / 1000), float(price)))
    return result


