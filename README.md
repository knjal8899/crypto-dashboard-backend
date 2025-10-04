# Crypto Dashboard Backend

A Django REST API backend for cryptocurrency dashboard with chat assistant functionality. This project fetches live cryptocurrency data from CoinGecko API and provides endpoints for dashboard data and a rule-based chat assistant.

## Features

- **Cryptocurrency Data Management**: Fetches and stores top cryptocurrencies with real-time price data
- **Historical Data**: Stores and provides historical price trends for the last 30 days
- **REST API Endpoints**: Clean, well-documented API endpoints for frontend integration
- **Chat Assistant**: Rule-based chat assistant that can answer questions about cryptocurrency prices, trends, and market data
- **Caching**: Redis-based caching for improved performance
- **Background Tasks**: Celery-based background tasks for data updates
- **Database**: PostgreSQL for reliable data storage

## API Endpoints

### Cryptocurrency Data
- `GET /api/v1/crypto/top-coins/` - Get top N cryptocurrencies
- `GET /api/v1/crypto/historical/` - Get historical price data for a coin
- `GET /api/v1/crypto/coin/<coin_id>/` - Get detailed information about a specific coin
- `GET /api/v1/crypto/market-data/` - Get global market data
- `GET /api/v1/crypto/search/` - Search for cryptocurrencies
- `POST /api/v1/crypto/refresh/` - Manually refresh cryptocurrency data

### Chat Assistant
- `POST /api/v1/chat/` - Send a message to the chat assistant
- `GET /api/v1/chat/sessions/` - List all chat sessions
- `POST /api/v1/chat/sessions/create/` - Create a new chat session
- `GET /api/v1/chat/sessions/<session_id>/` - Get chat session with messages
- `DELETE /api/v1/chat/sessions/<session_id>/` - Delete a chat session

## Chat Assistant Capabilities

The chat assistant can understand and respond to queries like:

- **Price Queries**: "What is the price of Bitcoin?", "How much is Ethereum worth?"
- **Trend Analysis**: "Show me the 7-day trend of Bitcoin", "How has Ethereum performed this month?"
- **Market Data**: "What's Bitcoin's market cap?", "What rank is Ethereum?"
- **Trading Volume**: "What's the trading volume of Bitcoin?"
- **Top Cryptocurrencies**: "Show me the top 10 cryptocurrencies"

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **API**: CoinGecko API for cryptocurrency data
- **Code Quality**: Black, Ruff, Pylint, MyPy

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- uv (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crypto-dashboard-backend
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb crypto_dashboard
   ```

5. **Run database migrations**
   ```bash
   cd src/crypto_dashboard_backend
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data**
   ```bash
   python manage.py update_crypto_data
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=crypto_dashboard
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# CoinGecko API (optional, for higher rate limits)
COINGECKO_API_KEY=your-coingecko-api-key-here

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### CoinGecko API Key

While the API works without a key, getting a free API key from [CoinGecko](https://www.coingecko.com/en/api) will provide higher rate limits.

## Running the Application

### Development Server

1. **Start Redis** (if not running as a service)
   ```bash
   redis-server
   ```

2. **Start Celery Worker** (in a separate terminal)
   ```bash
   cd src/crypto_dashboard_backend
   celery -A crypto_dashboard_backend worker --loglevel=info
   ```

3. **Start Celery Beat** (in a separate terminal, for periodic tasks)
   ```bash
   cd src/crypto_dashboard_backend
   celery -A crypto_dashboard_backend beat --loglevel=info
   ```

4. **Start Django Development Server**
   ```bash
   cd src/crypto_dashboard_backend
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

### Production Deployment

For production deployment, use a proper WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn crypto_dashboard_backend.wsgi:application --bind 0.0.0.0:8000
```

## Management Commands

- `python manage.py update_crypto_data` - Update cryptocurrency data
- `python manage.py shell` - Django shell
- `python manage.py collectstatic` - Collect static files

## API Usage Examples

### Get Top 10 Cryptocurrencies
```bash
curl "http://localhost:8000/api/v1/crypto/top-coins/?limit=10"
```

### Get Historical Data for Bitcoin
```bash
curl "http://localhost:8000/api/v1/crypto/historical/?coin_id=bitcoin&days=7"
```

### Chat with Assistant
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of Bitcoin?"}'
```

## Data Updates

The system automatically updates cryptocurrency data every 5 minutes via Celery tasks. You can also manually trigger updates:

```bash
curl -X POST "http://localhost:8000/api/v1/crypto/refresh/"
```

## Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **Ruff**: Fast linting
- **Pylint**: Comprehensive linting
- **MyPy**: Type checking

Run code quality checks:

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```
crypto-dashboard-backend/
├── src/
│   └── crypto_dashboard_backend/
│       ├── apps/
│       │   ├── crypto/           # Cryptocurrency data management
│       │   └── chat/             # Chat assistant functionality
│       ├── settings.py           # Django settings
│       ├── urls.py              # URL configuration
│       └── manage.py            # Django management script
├── pyproject.toml               # Project configuration
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run code quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue in the GitHub repository.
