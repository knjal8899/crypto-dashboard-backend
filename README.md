# 🚀 Crypto Dashboard Backend

A production-ready Django REST Framework backend for a cryptocurrency dashboard with AI chat assistant.

## 📋 Overview
- **Django 5 + DRF** backend with JWT authentication
- **Real-time crypto data** from CoinGecko API with caching
- **Rule-based chat assistant** for crypto queries
- **Watchlist functionality** with user preferences
- **Comprehensive API documentation** with Swagger UI
- **Production-ready** with Docker, security, and performance optimizations

## 🛠️ Tech Stack
- **Backend:** Django 5, Django REST Framework, SimpleJWT
- **Database:** PostgreSQL with optimized queries and pagination
- **Caching:** LocMem cache with configurable TTL
- **API Docs:** drf-spectacular (Swagger UI)
- **Deployment:** Docker, ASGI server (uvicorn)
- **Code Quality:** ruff, black, pylint
- **Package Management:** uv (fast Python package manager)

## 📋 Requirements
- **Python 3.12** (pinned by uv)
- **PostgreSQL** database
- **uv** package manager

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install uv
pip install uv

# Clone and setup
git clone <your-repo-url>
cd crypto-dashboard-backend
uv python pin 3.12
uv sync
```

### 2. Environment Configuration
Create `.env` file:
```dotenv
DJANGO_DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crypto_dashboard
CORS_ALLOWED_ORIGINS=http://localhost:3000
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7
COINGECKO_API_BASE=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=your-api-key-optional
COINGECKO_CACHE_TTL_SECONDS=300
API_PAGE_SIZE=10
```

### 3. Database Setup
```bash
# Create database
psql -U postgres -c "CREATE DATABASE crypto_dashboard;"

# Run migrations
uv run python src/manage.py migrate

# Create superuser
uv run python src/manage.py createsuperuser
```

### 4. Start Development Server
```bash
uv run python src/manage.py runserver 0.0.0.0:8000
```

**API Documentation:** http://localhost:8000/api/docs/

## 🐳 Docker Deployment
```bash
# Build and run with Docker Compose
docker compose up --build

# For production with external database
# Set DATABASE_URL in .env to your RDS/Cloud SQL endpoint
```

## 📚 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT tokens |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout and blacklist token |

### 💰 Cryptocurrency Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/coins/top?limit=10` | Get top cryptocurrencies |
| GET | `/api/coins/market-data` | Get global market data |
| GET | `/api/coins/gainers-losers` | Get top gainers and losers |
| GET | `/api/coins/{coin_id}/detail` | Get detailed coin information |
| GET | `/api/coins/{coin_id}/price-history?range=7d` | Get price chart data |
| GET | `/api/coins/{coin_id}/history?days=30` | Get historical data (legacy) |

### 📋 Watchlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/coins/watchlist` | Get user's watchlist |
| POST | `/api/coins/watchlist` | Add coin to watchlist |
| DELETE | `/api/coins/watchlist` | Remove coin from watchlist |

### 🤖 Chat Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/query?text=...` | Ask crypto questions |
| GET | `/api/chat/suggestions` | Get query suggestions |
| POST | `/api/chat/message` | Send message to assistant |

## 🧪 Testing
```bash
# Run all tests
uv run python src/manage.py test accounts coins chat -v 2

# Run specific app tests
uv run python src/manage.py test coins -v 2
```

## 🚀 Production Deployment

### AWS EC2 + RDS
1. **RDS Setup:** Create PostgreSQL instance
2. **EC2 Setup:** Launch Ubuntu instance with security groups
3. **Deploy:** Clone repo, install dependencies, configure environment
4. **Nginx:** Configure reverse proxy
5. **SSL:** Set up HTTPS with Let's Encrypt

### Environment Variables (Production)
```dotenv
DJANGO_DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com
COINGECKO_API_KEY=your-api-key
```

## 🔧 Features

### ✅ **Production Ready**
- JWT authentication with token blacklisting
- Comprehensive API documentation (Swagger UI)
- Database optimization with pagination and select_related
- Caching strategy for external API calls
- Error handling with graceful fallbacks
- Security best practices (CORS, input validation)
- Docker containerization

### ✅ **Performance Optimized**
- Database query optimization
- API response caching
- Pagination for large datasets
- Efficient serialization
- Connection pooling ready

### ✅ **Developer Friendly**
- Interactive API documentation
- Comprehensive error messages
- Consistent response formats
- Unit tests coverage
- Clean code architecture

## 📝 Commit Convention
```
FEAT: add new feature
FIX: fix bug or issue
CHORE: maintenance tasks
PERF: performance improvements
```

## 🔗 References
- [Django REST Framework](https://www.django-rest-framework.org/)
- [CoinGecko API](https://docs.coingecko.com/v3.0.1/reference/coins-list)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)