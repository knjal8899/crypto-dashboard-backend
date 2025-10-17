from django.db import models
from django.contrib.auth.models import User


class Coin(models.Model):
    cg_id = models.CharField(max_length=128, unique=True)
    symbol = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    last_price_usd = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last_volume_24h_usd = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    last_pct_change_24h = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    market_cap_rank = models.IntegerField(null=True, blank=True)
    market_cap_usd = models.DecimalField(max_digits=24, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    last_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["last_updated_at"]),
        ]


class PriceHistory(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name="history")
    date = models.DateField()
    price_usd = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ("coin", "date")
        ordering = ["date"]
        indexes = [
            models.Index(fields=["coin", "date"]),
        ]


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name="watchers")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin")
        ordering = ["-added_at"]
        indexes = [
            models.Index(fields=["user", "coin"]),
        ]

    def __str__(self):
        return f"{self.user.username} watches {self.coin.name}"


class Meta:
    pass


