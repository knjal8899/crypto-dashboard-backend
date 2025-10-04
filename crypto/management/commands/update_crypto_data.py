from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from crypto.models import Coin, PriceHistory
from crypto.services import fetch_top_coins_market_data, fetch_coin_market_chart


class Command(BaseCommand):
    help = "Fetch top coins and 30-day history from CoinGecko and store in DB"

    def add_arguments(self, parser):
        parser.add_argument("--per-page", type=int, default=10)
        parser.add_argument("--days", type=int, default=30)

    def handle(self, *args, **options):
        per_page: int = options["per_page"]
        days: int = options["days"]

        markets = fetch_top_coins_market_data(per_page=per_page)

        with transaction.atomic():
            for m in markets:
                coin, _ = Coin.objects.update_or_create(
                    coingecko_id=m.id,
                    defaults={
                        "symbol": m.symbol,
                        "name": m.name,
                        "price_usd": m.current_price,
                        "volume_24h_usd": m.total_volume,
                        "percent_change_24h": m.price_change_percentage_24h,
                    },
                )

                history = fetch_coin_market_chart(coin_id=m.id, days=days)
                for ts, price in history:
                    PriceHistory.objects.update_or_create(
                        coin=coin, timestamp=ts, defaults={"price_usd": price}
                    )

        self.stdout.write(self.style.SUCCESS("Crypto data updated successfully"))


