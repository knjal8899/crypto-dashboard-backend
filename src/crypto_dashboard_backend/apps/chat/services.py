"""
Services for chat assistant functionality.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache

from apps.crypto.models import Cryptocurrency, PriceHistory
from apps.crypto.services import CryptoDataService

logger = logging.getLogger(__name__)


class ChatAssistantService:
    """Service for processing chat messages and generating responses."""
    
    def __init__(self):
        self.crypto_service = CryptoDataService()
        
        # Common cryptocurrency names and their CoinGecko IDs
        self.crypto_aliases = {
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'binance coin': 'binancecoin',
            'bnb': 'binancecoin',
            'cardano': 'cardano',
            'ada': 'cardano',
            'solana': 'solana',
            'sol': 'solana',
            'polkadot': 'polkadot',
            'dot': 'polkadot',
            'dogecoin': 'dogecoin',
            'doge': 'dogecoin',
            'avalanche': 'avalanche-2',
            'avax': 'avalanche-2',
            'chainlink': 'chainlink',
            'link': 'chainlink',
            'litecoin': 'litecoin',
            'ltc': 'litecoin',
            'polygon': 'matic-network',
            'matic': 'matic-network',
        }
    
    def process_message(self, message: str, session_id: str) -> Dict:
        """Process a user message and generate a response."""
        try:
            # Normalize the message
            normalized_message = message.lower().strip()
            
            # Determine the intent and extract parameters
            intent, params = self._parse_intent(normalized_message)
            
            # Generate response based on intent
            response = self._generate_response(intent, params, normalized_message)
            
            return {
                'response': response,
                'session_id': session_id,
                'message_type': 'assistant',
                'timestamp': timezone.now(),
            }
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I'm sorry, I encountered an error processing your request. Please try again.",
                'session_id': session_id,
                'message_type': 'assistant',
                'timestamp': timezone.now(),
            }
    
    def _parse_intent(self, message: str) -> Tuple[str, Dict]:
        """Parse user intent from the message."""
        # Price queries
        if any(keyword in message for keyword in ['price', 'cost', 'value', 'worth']):
            coin_name = self._extract_coin_name(message)
            if coin_name:
                return 'price', {'coin': coin_name}
        
        # Trend queries
        if any(keyword in message for keyword in ['trend', 'chart', 'graph', 'performance', 'change']):
            coin_name = self._extract_coin_name(message)
            days = self._extract_days(message)
            return 'trend', {'coin': coin_name, 'days': days}
        
        # Market cap queries
        if any(keyword in message for keyword in ['market cap', 'marketcap', 'ranking', 'rank']):
            coin_name = self._extract_coin_name(message)
            return 'market_cap', {'coin': coin_name}
        
        # Volume queries
        if any(keyword in message for keyword in ['volume', 'trading volume']):
            coin_name = self._extract_coin_name(message)
            return 'volume', {'coin': coin_name}
        
        # Top coins queries
        if any(keyword in message for keyword in ['top', 'best', 'popular', 'leading']):
            limit = self._extract_number(message) or 10
            return 'top_coins', {'limit': limit}
        
        # Help queries
        if any(keyword in message for keyword in ['help', 'what can you do', 'commands']):
            return 'help', {}
        
        # Greeting queries
        if any(keyword in message for keyword in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting', {}
        
        # Default to general response
        return 'general', {}
    
    def _extract_coin_name(self, message: str) -> Optional[str]:
        """Extract cryptocurrency name from the message."""
        # Check for exact matches in aliases
        for alias, coin_id in self.crypto_aliases.items():
            if alias in message:
                return coin_id
        
        # Try to find coin names in the message
        # Look for patterns like "price of X" or "X price"
        patterns = [
            r'price of (\w+)',
            r'(\w+) price',
            r'value of (\w+)',
            r'(\w+) value',
            r'cost of (\w+)',
            r'(\w+) cost',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                coin_name = match.group(1).lower()
                if coin_name in self.crypto_aliases:
                    return self.crypto_aliases[coin_name]
        
        return None
    
    def _extract_days(self, message: str) -> int:
        """Extract number of days from the message."""
        # Look for patterns like "7 day", "30 day", "1 week", etc.
        patterns = [
            r'(\d+)\s*day',
            r'(\d+)\s*week',
            r'(\d+)\s*month',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                days = int(match.group(1))
                if 'week' in pattern:
                    days *= 7
                elif 'month' in pattern:
                    days *= 30
                return min(days, 365)  # Cap at 1 year
        
        # Default to 7 days for trend queries
        return 7
    
    def _extract_number(self, message: str) -> Optional[int]:
        """Extract a number from the message."""
        match = re.search(r'(\d+)', message)
        return int(match.group(1)) if match else None
    
    def _generate_response(self, intent: str, params: Dict, original_message: str) -> str:
        """Generate response based on intent and parameters."""
        if intent == 'price':
            return self._handle_price_query(params)
        elif intent == 'trend':
            return self._handle_trend_query(params)
        elif intent == 'market_cap':
            return self._handle_market_cap_query(params)
        elif intent == 'volume':
            return self._handle_volume_query(params)
        elif intent == 'top_coins':
            return self._handle_top_coins_query(params)
        elif intent == 'help':
            return self._handle_help_query()
        elif intent == 'greeting':
            return self._handle_greeting()
        else:
            return self._handle_general_query(original_message)
    
    def _handle_price_query(self, params: Dict) -> str:
        """Handle price-related queries."""
        coin = params.get('coin')
        if not coin:
            return "I need to know which cryptocurrency you're asking about. Please specify the coin name or symbol."
        
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin)
            price = cryptocurrency.current_price
            change_24h = cryptocurrency.price_change_percentage_24h
            
            response = f"The current price of {cryptocurrency.name} ({cryptocurrency.symbol.upper()}) is ${price:,.2f}"
            
            if change_24h is not None:
                change_text = "increased" if change_24h >= 0 else "decreased"
                response += f". It has {change_text} by {abs(change_24h):.2f}% in the last 24 hours."
            
            return response
        except Cryptocurrency.DoesNotExist:
            return f"I couldn't find information about {coin}. Please check the spelling or try a different cryptocurrency."
    
    def _handle_trend_query(self, params: Dict) -> str:
        """Handle trend-related queries."""
        coin = params.get('coin')
        days = params.get('days', 7)
        
        if not coin:
            return "I need to know which cryptocurrency you're asking about for the trend analysis."
        
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin)
            
            # Get historical data
            historical_data = self.crypto_service.get_historical_data_from_db(coin, days)
            
            if not historical_data:
                return f"I don't have enough historical data for {cryptocurrency.name} for the last {days} days."
            
            # Calculate trend
            prices = [float(h.price) for h in historical_data]
            if len(prices) < 2:
                return f"I need more data points to analyze the trend for {cryptocurrency.name}."
            
            start_price = prices[0]
            end_price = prices[-1]
            change_percent = ((end_price - start_price) / start_price) * 100
            
            trend = "increased" if change_percent >= 0 else "decreased"
            
            return f"Over the last {days} days, {cryptocurrency.name} has {trend} by {abs(change_percent):.2f}%. The price moved from ${start_price:,.2f} to ${end_price:,.2f}."
        except Cryptocurrency.DoesNotExist:
            return f"I couldn't find information about {coin}. Please check the spelling or try a different cryptocurrency."
    
    def _handle_market_cap_query(self, params: Dict) -> str:
        """Handle market cap queries."""
        coin = params.get('coin')
        if not coin:
            return "I need to know which cryptocurrency you're asking about for market cap information."
        
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin)
            market_cap = cryptocurrency.market_cap
            rank = cryptocurrency.market_cap_rank
            
            response = f"{cryptocurrency.name} has a market cap of ${market_cap:,.0f}"
            
            if rank:
                response += f" and is ranked #{rank} by market capitalization."
            
            return response
        except Cryptocurrency.DoesNotExist:
            return f"I couldn't find information about {coin}. Please check the spelling or try a different cryptocurrency."
    
    def _handle_volume_query(self, params: Dict) -> str:
        """Handle volume queries."""
        coin = params.get('coin')
        if not coin:
            return "I need to know which cryptocurrency you're asking about for volume information."
        
        try:
            cryptocurrency = Cryptocurrency.objects.get(coin_id=coin)
            volume = cryptocurrency.total_volume
            
            return f"The 24-hour trading volume for {cryptocurrency.name} is ${volume:,.0f}."
        except Cryptocurrency.DoesNotExist:
            return f"I couldn't find information about {coin}. Please check the spelling or try a different cryptocurrency."
    
    def _handle_top_coins_query(self, params: Dict) -> str:
        """Handle top coins queries."""
        limit = params.get('limit', 10)
        
        try:
            coins = self.crypto_service.get_top_coins_from_db(limit)
            
            if not coins:
                return "I don't have current data about the top cryptocurrencies. Please try again later."
            
            response = f"Here are the top {len(coins)} cryptocurrencies by market cap:\n\n"
            
            for i, coin in enumerate(coins, 1):
                response += f"{i}. {coin.name} ({coin.symbol.upper()}) - ${coin.current_price:,.2f}"
                if coin.price_change_percentage_24h is not None:
                    change_text = "+" if coin.price_change_percentage_24h >= 0 else ""
                    response += f" ({change_text}{coin.price_change_percentage_24h:.2f}%)"
                response += "\n"
            
            return response
        except Exception as e:
            logger.error(f"Error handling top coins query: {e}")
            return "I encountered an error while fetching the top cryptocurrencies. Please try again later."
    
    def _handle_help_query(self) -> str:
        """Handle help queries."""
        return """I'm a cryptocurrency assistant! Here's what I can help you with:

💰 **Price Information**: Ask about the current price of any cryptocurrency
   Example: "What is the price of Bitcoin?" or "How much is Ethereum worth?"

📈 **Trend Analysis**: Get price trends and performance over time
   Example: "Show me the 7-day trend of Bitcoin" or "How has Ethereum performed this month?"

🏆 **Market Cap & Ranking**: Learn about market capitalization and rankings
   Example: "What's Bitcoin's market cap?" or "What rank is Ethereum?"

📊 **Trading Volume**: Check 24-hour trading volumes
   Example: "What's the trading volume of Bitcoin?"

🥇 **Top Cryptocurrencies**: Get lists of top-performing coins
   Example: "Show me the top 10 cryptocurrencies" or "What are the best coins?"

Just ask me naturally - I understand various ways of phrasing questions!"""
    
    def _handle_greeting(self) -> str:
        """Handle greeting queries."""
        return """Hello! 👋 I'm your cryptocurrency assistant. I can help you with:

• Current prices of cryptocurrencies
• Price trends and performance analysis
• Market cap and ranking information
• Trading volume data
• Top cryptocurrency lists

What would you like to know about cryptocurrencies today?"""
    
    def _handle_general_query(self, message: str) -> str:
        """Handle general queries that don't match specific intents."""
        return f"""I'm not sure how to help with "{message}". 

I'm specialized in cryptocurrency information. You can ask me about:
• Current prices (e.g., "What's the price of Bitcoin?")
• Price trends (e.g., "Show me Bitcoin's 7-day trend")
• Market data (e.g., "What's Ethereum's market cap?")
• Top cryptocurrencies (e.g., "Show me the top 10 coins")

Type "help" for more detailed examples!"""
