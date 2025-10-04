"""
Models for cryptocurrency data storage.
"""

from django.db import models
from django.core.validators import MinValueValidator


class Cryptocurrency(models.Model):
    """Model to store cryptocurrency information."""
    
    coin_id = models.CharField(max_length=100, unique=True, db_index=True)
    symbol = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    current_price = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        validators=[MinValueValidator(0)]
    )
    market_cap = models.BigIntegerField(null=True, blank=True)
    total_volume = models.BigIntegerField(null=True, blank=True)
    price_change_24h = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True
    )
    price_change_percentage_24h = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True
    )
    market_cap_rank = models.PositiveIntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['market_cap_rank', 'name']
        verbose_name = 'Cryptocurrency'
        verbose_name_plural = 'Cryptocurrencies'
    
    def __str__(self):
        return f"{self.name} ({self.symbol.upper()})"


class PriceHistory(models.Model):
    """Model to store historical price data for cryptocurrencies."""
    
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, 
        on_delete=models.CASCADE, 
        related_name='price_history'
    )
    price = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        validators=[MinValueValidator(0)]
    )
    market_cap = models.BigIntegerField(null=True, blank=True)
    total_volume = models.BigIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['cryptocurrency', 'timestamp']
        verbose_name = 'Price History'
        verbose_name_plural = 'Price Histories'
    
    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.price} at {self.timestamp}"


class MarketData(models.Model):
    """Model to store overall market data."""
    
    total_market_cap = models.BigIntegerField()
    total_volume = models.BigIntegerField()
    active_cryptocurrencies = models.PositiveIntegerField()
    market_cap_percentage_btc = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    market_cap_percentage_eth = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Market Data'
        verbose_name_plural = 'Market Data'
    
    def __str__(self):
        return f"Market Data - {self.timestamp}"
