"""
Management command to update cryptocurrency data.
"""

from django.core.management.base import BaseCommand
from apps.crypto.services import CryptoDataService


class Command(BaseCommand):
    """Command to update cryptocurrency data from CoinGecko API."""
    
    help = 'Update cryptocurrency data from CoinGecko API'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--top-coins',
            type=int,
            default=50,
            help='Number of top coins to update (default: 50)'
        )
        parser.add_argument(
            '--historical-days',
            type=int,
            default=30,
            help='Number of days of historical data to fetch (default: 30)'
        )
        parser.add_argument(
            '--skip-historical',
            action='store_true',
            help='Skip updating historical data'
        )
        parser.add_argument(
            '--skip-global',
            action='store_true',
            help='Skip updating global market data'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.stdout.write('Starting cryptocurrency data update...')
        
        crypto_service = CryptoDataService()
        
        # Update top coins
        self.stdout.write(f'Updating top {options["top_coins"]} coins...')
        top_coins_success = crypto_service.update_top_coins(options['top_coins'])
        
        if top_coins_success:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated top {options["top_coins"]} coins')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to update top coins')
            )
        
        # Update global market data
        if not options['skip_global']:
            self.stdout.write('Updating global market data...')
            global_success = crypto_service.update_global_market_data()
            
            if global_success:
                self.stdout.write(
                    self.style.SUCCESS('Successfully updated global market data')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to update global market data')
                )
        
        # Update historical data
        if not options['skip_historical']:
            self.stdout.write('Updating historical data...')
            top_coins = crypto_service.get_top_coins_from_db(10)
            historical_success_count = 0
            
            for coin in top_coins:
                self.stdout.write(f'Updating historical data for {coin.name}...')
                if crypto_service.update_historical_data(coin.coin_id, options['historical_days']):
                    historical_success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully updated historical data for {coin.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to update historical data for {coin.name}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Historical data update completed: {historical_success_count}/{len(top_coins)} coins'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('Cryptocurrency data update completed!')
        )
