import os
from typing import Any, Dict, List
import requests
from django.core.cache import cache
from django.conf import settings

COINGECKO_API_BASE = os.getenv("COINGECKO_API_BASE", "https://api.coingecko.com/api/v3")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")


def _headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return headers


def fetch_top_coins(limit: int = 10) -> List[Dict[str, Any]]:
    cache_key = f"coingecko_top_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    resp = requests.get(url, params=params, headers=_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    cache.set(cache_key, data, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
    return data


def fetch_coin_history(coin_id: str, days: int = 30) -> Dict[str, Any]:
    cache_key = f"coingecko_hist_{coin_id}_{days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    resp = requests.get(url, params=params, headers=_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    cache.set(cache_key, data, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
    return data


def fetch_coin_market_by_id(coin_id: str) -> Dict[str, Any]:
    cache_key = f"coingecko_market_{coin_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": coin_id,
        "sparkline": "false",
    }
    resp = requests.get(url, params=params, headers=_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    item = data[0] if isinstance(data, list) and data else {}
    cache.set(cache_key, item, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
    return item
