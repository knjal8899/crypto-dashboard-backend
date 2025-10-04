"""
Views for cryptocurrency data endpoints.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .models import Cryptocurrency, PriceHistory, MarketData
from .serializers import (
    CryptocurrencySerializer,
    PriceHistorySerializer,
    MarketDataSerializer,
    TopCoinsSerializer,
    HistoricalDataSerializer,
)
from .services import CryptoDataService


class TopCoinsView(APIView):
    """API view for getting top N cryptocurrencies."""
    
    def get(self, request):
        """Get top N cryptocurrencies."""
        serializer = TopCoinsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        limit = serializer.validated_data['limit']
        sort_by = serializer.validated_data['sort_by']
        
        # Try to get from cache first
        cache_key = f'top_coins_{limit}_{sort_by}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get from database
        crypto_service = CryptoDataService()
        coins = crypto_service.get_top_coins_from_db(limit, sort_by)
        
        if not coins:
            # If no data in database, fetch from API
            success = crypto_service.update_top_coins(limit)
            if success:
                coins = crypto_service.get_top_coins_from_db(limit, sort_by)
            else:
                return Response(
                    {'error': 'Unable to fetch cryptocurrency data'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        serializer = CryptocurrencySerializer(coins, many=True)
        response_data = serializer.data
        
        # Cache the response for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)


class HistoricalDataView(APIView):
    """API view for getting historical price data."""
    
    def get(self, request):
        """Get historical price data for a cryptocurrency."""
        serializer = HistoricalDataSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        coin_id = serializer.validated_data['coin_id']
        days = serializer.validated_data['days']
        
        # Try to get from cache first
        cache_key = f'historical_data_{coin_id}_{days}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get from database
        crypto_service = CryptoDataService()
        historical_data = crypto_service.get_historical_data_from_db(coin_id, days)
        
        if not historical_data:
            # If no data in database, fetch from API
            success = crypto_service.update_historical_data(coin_id, days)
            if success:
                historical_data = crypto_service.get_historical_data_from_db(coin_id, days)
            else:
                return Response(
                    {'error': f'Unable to fetch historical data for {coin_id}'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        serializer = PriceHistorySerializer(historical_data, many=True)
        response_data = serializer.data
        
        # Cache the response for 30 minutes
        cache.set(cache_key, response_data, 1800)
        
        return Response(response_data)


class CoinDetailView(APIView):
    """API view for getting detailed information about a specific coin."""
    
    def get(self, request, coin_id):
        """Get detailed information about a cryptocurrency."""
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin_id)
            serializer = CryptocurrencySerializer(cryptocurrency)
            return Response(serializer.data)
        except Cryptocurrency.DoesNotExist:
            return Response(
                {'error': f'Cryptocurrency with ID {coin_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarketDataView(APIView):
    """API view for getting global market data."""
    
    def get(self, request):
        """Get global cryptocurrency market data."""
        # Try to get from cache first
        cache_key = 'global_market_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get latest market data from database
        market_data = MarketData.objects.first()
        
        if not market_data:
            # If no data in database, fetch from API
            crypto_service = CryptoDataService()
            success = crypto_service.update_global_market_data()
            if success:
                market_data = MarketData.objects.first()
            else:
                return Response(
                    {'error': 'Unable to fetch global market data'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        serializer = MarketDataSerializer(market_data)
        response_data = serializer.data
        
        # Cache the response for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)


@api_view(['POST'])
def refresh_data(request):
    """Endpoint to manually refresh cryptocurrency data."""
    crypto_service = CryptoDataService()
    
    # Update top coins
    top_coins_success = crypto_service.update_top_coins(50)
    
    # Update global market data
    global_data_success = crypto_service.update_global_market_data()
    
    # Update historical data for top 10 coins
    top_coins = crypto_service.get_top_coins_from_db(10)
    historical_success_count = 0
    
    for coin in top_coins:
        if crypto_service.update_historical_data(coin.coin_id, 30):
            historical_success_count += 1
    
    return Response({
        'message': 'Data refresh completed',
        'top_coins_updated': top_coins_success,
        'global_data_updated': global_data_success,
        'historical_data_updated': f"{historical_success_count}/{len(top_coins)} coins",
    })


@api_view(['GET'])
def search_coins(request):
    """Search for cryptocurrencies by name or symbol."""
    query = request.query_params.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response(
            {'error': 'Query parameter "q" is required and must be at least 2 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search in database
    coins = Cryptocurrency.objects.filter(
        models.Q(name__icontains=query) | 
        models.Q(symbol__icontains=query) |
        models.Q(coin_id__icontains=query)
    )[:20]
    
    serializer = CryptocurrencySerializer(coins, many=True)
    return Response(serializer.data)
