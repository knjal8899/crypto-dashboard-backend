from django.db import models


class Coin(models.Model):
    coingecko_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=30)
    name = models.CharField(max_length=100)

    # latest snapshot fields for convenience
    price_usd = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    volume_24h_usd = models.DecimalField(max_digits=24, decimal_places=8, null=True, blank=True)
    percent_change_24h = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["coingecko_id"]),
            models.Index(fields=["symbol"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"


class PriceHistory(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name="prices")
    timestamp = models.DateTimeField()
    price_usd = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ("coin", "timestamp")
        indexes = [
            models.Index(fields=["coin", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.coin.symbol}@{self.timestamp.isoformat()}={self.price_usd}"

# Create your models here.
