"""
Services for cryptocurrency data management.
"""

import requests
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import Cryptocurrency, PriceHistory, MarketData

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key
            })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to CoinGecko API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed: {e}")
            return None
    
    def get_coins_list(self) -> Optional[List[Dict]]:
        """Get list of all supported coins."""
        cache_key = 'coingecko_coins_list'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request('coins/list')
        if data:
            cache.set(cache_key, data, 1800)  # Cache for 30 minutes
        return data
    
    def get_top_coins(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get top coins by market cap."""
        cache_key = f'coingecko_top_coins_{limit}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        data = self._make_request('coins/markets', params)
        if data:
            cache.set(cache_key, data, 300)  # Cache for 5 minutes
        return data
    
    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Get detailed data for a specific coin."""
        cache_key = f'coingecko_coin_data_{coin_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request(f'coins/{coin_id}')
        if data:
            cache.set(cache_key, data, 300)  # Cache for 5 minutes
        return data
    
    def get_historical_data(
        self, 
        coin_id: str, 
        days: int = 30
    ) -> Optional[List[List]]:
        """Get historical price data for a coin."""
        cache_key = f'coingecko_historical_{coin_id}_{days}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        data = self._make_request(f'coins/{coin_id}/market_chart', params)
        if data and 'prices' in data:
            cache.set(cache_key, data['prices'], 1800)  # Cache for 30 minutes
            return data['prices']
        return None
    
    def get_global_data(self) -> Optional[Dict]:
        """Get global cryptocurrency market data."""
        cache_key = 'coingecko_global_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request('global')
        if data and 'data' in data:
            cache.set(cache_key, data['data'], 300)  # Cache for 5 minutes
            return data['data']
        return None


class CryptoDataService:
    """Service for managing cryptocurrency data in the database."""
    
    def __init__(self):
        self.coingecko_service = CoinGeckoService()
    
    def update_top_coins(self, limit: int = 10) -> bool:
        """Update top coins data in the database."""
        try:
            coins_data = self.coingecko_service.get_top_coins(limit)
            if not coins_data:
                return False
            
            for coin_data in coins_data:
                self._update_or_create_cryptocurrency(coin_data)
            
            logger.info(f"Updated {len(coins_data)} top coins")
            return True
        except Exception as e:
            logger.error(f"Failed to update top coins: {e}")
            return False
    
    def update_historical_data(self, coin_id: str, days: int = 30) -> bool:
        """Update historical data for a specific coin."""
        try:
            historical_data = self.coingecko_service.get_historical_data(coin_id, days)
            if not historical_data:
                return False
            
            try:
                cryptocurrency = Cryptocurrency.objects.get(coin_id=coin_id)
            except Cryptocurrency.DoesNotExist:
                logger.error(f"Cryptocurrency with coin_id {coin_id} not found")
                return False
            
            # Clear existing historical data for the specified period
            cutoff_date = timezone.now() - timedelta(days=days)
            PriceHistory.objects.filter(
                cryptocurrency=cryptocurrency,
                timestamp__gte=cutoff_date
            ).delete()
            
            # Create new historical data entries
            price_histories = []
            for price_data in historical_data:
                timestamp = datetime.fromtimestamp(price_data[0] / 1000, tz=timezone.utc)
                price = Decimal(str(price_data[1]))
                
                price_histories.append(PriceHistory(
                    cryptocurrency=cryptocurrency,
                    price=price,
                    timestamp=timestamp
                ))
            
            PriceHistory.objects.bulk_create(price_histories, ignore_conflicts=True)
            
            logger.info(f"Updated historical data for {coin_id}: {len(price_histories)} entries")
            return True
        except Exception as e:
            logger.error(f"Failed to update historical data for {coin_id}: {e}")
            return False
    
    def update_global_market_data(self) -> bool:
        """Update global market data."""
        try:
            global_data = self.coingecko_service.get_global_data()
            if not global_data:
                return False
            
            market_data = MarketData.objects.create(
                total_market_cap=global_data.get('total_market_cap', {}).get('usd', 0),
                total_volume=global_data.get('total_volume', {}).get('usd', 0),
                active_cryptocurrencies=global_data.get('active_cryptocurrencies', 0),
                market_cap_percentage_btc=global_data.get('market_cap_percentage', {}).get('btc'),
                market_cap_percentage_eth=global_data.get('market_cap_percentage', {}).get('eth'),
            )
            
            logger.info("Updated global market data")
            return True
        except Exception as e:
            logger.error(f"Failed to update global market data: {e}")
            return False
    
    def _update_or_create_cryptocurrency(self, coin_data: Dict) -> Cryptocurrency:
        """Update or create a cryptocurrency record."""
        defaults = {
            'symbol': coin_data.get('symbol', '').upper(),
            'name': coin_data.get('name', ''),
            'image_url': coin_data.get('image', ''),
            'current_price': Decimal(str(coin_data.get('current_price', 0))),
            'market_cap': coin_data.get('market_cap'),
            'total_volume': coin_data.get('total_volume'),
            'price_change_24h': coin_data.get('price_change_24h'),
            'price_change_percentage_24h': coin_data.get('price_change_percentage_24h'),
            'market_cap_rank': coin_data.get('market_cap_rank'),
        }
        
        cryptocurrency, created = Cryptocurrency.objects.update_or_create(
            coin_id=coin_data.get('id'),
            defaults=defaults
        )
        
        return cryptocurrency
    
    def get_top_coins_from_db(self, limit: int = 10, sort_by: str = 'market_cap_rank') -> List[Cryptocurrency]:
        """Get top coins from database."""
        queryset = Cryptocurrency.objects.all()
        
        if sort_by == 'market_cap_rank':
            queryset = queryset.order_by('market_cap_rank')
        elif sort_by == 'market_cap':
            queryset = queryset.order_by('-market_cap')
        elif sort_by == 'price_change_percentage_24h':
            queryset = queryset.order_by('-price_change_percentage_24h')
        elif sort_by == 'total_volume':
            queryset = queryset.order_by('-total_volume')
        
        return queryset[:limit]
    
    def get_historical_data_from_db(
        self, 
        coin_id: str, 
        days: int = 30
    ) -> Optional[List[PriceHistory]]:
        """Get historical data from database."""
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin_id)
            cutoff_date = timezone.now() - timedelta(days=days)
            
            return PriceHistory.objects.filter(
                cryptocurrency=cryptocurrency,
                timestamp__gte=cutoff_date
            ).order_by('timestamp')
        except Cryptocurrency.DoesNotExist:
            return None
