"""
Celery tasks for cryptocurrency data management.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import CryptoDataService

logger = logging.getLogger(__name__)


@shared_task
def update_crypto_data():
    """Periodic task to update cryptocurrency data."""
    logger.info("Starting periodic cryptocurrency data update")
    
    crypto_service = CryptoDataService()
    
    # Update top 50 coins
    top_coins_success = crypto_service.update_top_coins(50)
    logger.info(f"Top coins update: {'Success' if top_coins_success else 'Failed'}")
    
    # Update global market data
    global_success = crypto_service.update_global_market_data()
    logger.info(f"Global market data update: {'Success' if global_success else 'Failed'}")
    
    # Update historical data for top 10 coins
    top_coins = crypto_service.get_top_coins_from_db(10)
    historical_success_count = 0
    
    for coin in top_coins:
        if crypto_service.update_historical_data(coin.coin_id, 30):
            historical_success_count += 1
    
    logger.info(f"Historical data update: {historical_success_count}/{len(top_coins)} coins")
    
    return {
        'top_coins_updated': top_coins_success,
        'global_data_updated': global_success,
        'historical_data_updated': f"{historical_success_count}/{len(top_coins)} coins",
        'timestamp': timezone.now().isoformat(),
    }


@shared_task
def update_historical_data_for_coin(coin_id: str, days: int = 30):
    """Task to update historical data for a specific coin."""
    logger.info(f"Updating historical data for {coin_id} ({days} days)")
    
    crypto_service = CryptoDataService()
    success = crypto_service.update_historical_data(coin_id, days)
    
    if success:
        logger.info(f"Successfully updated historical data for {coin_id}")
    else:
        logger.error(f"Failed to update historical data for {coin_id}")
    
    return {
        'coin_id': coin_id,
        'days': days,
        'success': success,
        'timestamp': timezone.now().isoformat(),
    }


@shared_task
def cleanup_old_data():
    """Task to cleanup old data."""
    logger.info("Starting data cleanup")
    
    from .models import PriceHistory, MarketData
    
    # Delete price history older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_history = PriceHistory.objects.filter(timestamp__lt=cutoff_date).delete()
    logger.info(f"Deleted {deleted_history[0]} old price history records")
    
    # Keep only the latest 100 market data records
    market_data_count = MarketData.objects.count()
    if market_data_count > 100:
        old_records = MarketData.objects.order_by('timestamp')[:market_data_count - 100]
        deleted_market = old_records.delete()
        logger.info(f"Deleted {deleted_market[0]} old market data records")
    
    return {
        'deleted_history_records': deleted_history[0],
        'deleted_market_records': deleted_market[0] if market_data_count > 100 else 0,
        'timestamp': timezone.now().isoformat(),
    }
