from django.db import models


class Coin(models.Model):
    cg_id = models.CharField(max_length=128, unique=True)
    symbol = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    last_price_usd = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class PriceHistory(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name="history")
    date = models.DateField()
    price_usd = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ("coin", "date")
        ordering = ["date"]


# Create your models here.
