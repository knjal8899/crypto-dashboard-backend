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


def fetch_global_market_data() -> Dict[str, Any]:
    """Fetch global cryptocurrency market data including Bitcoin dominance"""
    cache_key = "coingecko_global"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        url = f"{COINGECKO_API_BASE}/global"
        resp = requests.get(url, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
        return data
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        # Return mock data if API fails
        return {
            "data": {
                "total_market_cap": {"usd": 253770000000000},
                "total_volume": {"usd": 357970000000},
                "market_cap_change_percentage_24h_usd": 2.51,
                "active_cryptocurrencies": 25,
                "market_cap_percentage": {"btc": 45.67}
            }
        }


def fetch_coin_detailed_info(coin_id: str) -> Dict[str, Any]:
    """Fetch detailed information about a specific coin"""
    cache_key = f"coingecko_coin_detail_{coin_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }
        resp = requests.get(url, params=params, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
        return data
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        # Return mock data if API fails
        return {
            "id": coin_id,
            "name": coin_id.title(),
            "symbol": coin_id[:4].upper(),
            "image": {"large": "https://via.placeholder.com/200x200"},
            "market_data": {
                "current_price": {"usd": 1000.0},
                "market_cap": {"usd": 1000000000},
                "total_volume": {"usd": 100000000},
                "price_change_percentage_24h": 0.0,
                "price_change_percentage_7d": 0.0,
                "price_change_percentage_30d": 0.0,
                "market_cap_rank": 1,
                "circulating_supply": 1000000,
                "total_supply": 1000000,
                "max_supply": 1000000,
                "ath": {"usd": 2000.0},
                "atl": {"usd": 500.0}
            }
        }


def fetch_coin_chart_data(coin_id: str, days: int = 7) -> Dict[str, Any]:
    """Fetch comprehensive chart data for a coin including prices, volumes, and market caps"""
    cache_key = f"coingecko_chart_{coin_id}_{days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily" if days > 1 else "hourly"
        }
        resp = requests.get(url, params=params, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, getattr(settings, "COINGECKO_CACHE_TTL_SECONDS", 300))
        return data
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        # Return mock data if API fails
        import time
        current_time = int(time.time() * 1000)
        mock_prices = []
        mock_volumes = []
        mock_market_caps = []
        
        base_price = 1000.0
        for i in range(days):
            timestamp = current_time - (days - i) * 24 * 60 * 60 * 1000
            price = base_price + (i * 10) + (i % 3 - 1) * 50
            volume = 1000000 + (i * 10000)
            market_cap = price * 1000000
            
            mock_prices.append([timestamp, price])
            mock_volumes.append([timestamp, volume])
            mock_market_caps.append([timestamp, market_cap])
        
        return {
            "prices": mock_prices,
            "total_volumes": mock_volumes,
            "market_caps": mock_market_caps
        }
