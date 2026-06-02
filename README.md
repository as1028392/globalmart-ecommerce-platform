# GlobalMart E-Commerce Platform

A production-ready cross-border e-commerce platform connecting Egyptian consumers with global markets.

## Features

- **Global Product Access**: Connect to AliExpress, Turkish textile factories, and Korean beauty platforms
- **Dynamic Pricing Engine**: Real-time USD to EGP conversion with transparent fee breakdown
- **Local Payment Methods**: Vodafone Cash, Meeza cards, Visa/Mastercard via Paymob & Fawry
- **Smart Logistics**: International shipping (Aramex) + domestic delivery (Bosta)
- **Real-time Notifications**: SMS (Twilio) and push notifications (Firebase)
- **Encrypted Data Storage**: All sensitive user data encrypted at rest

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (Recommended)

```bash
# 1. Clone and enter directory
cd ecommerce-platform

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Access application
# Frontend: http://localhost
# API: http://localhost/api/v1
# API Docs: http://localhost/api/v1/docs
```

### Local Development

```bash
# Terminal 1: Database & Cache
docker-compose up -d postgres redis

# Terminal 2: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
ecommerce-platform/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # API Routes
│   │   ├── core/        # Config & Security
│   │   ├── models/      # Database Models
│   │   ├── services/    # Business Logic
│   │   └── integrations/# External APIs
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React.js Storefront
│   ├── src/
│   │   ├── components/  # React Components
│   │   ├── pages/       # Page Components
│   │   ├── services/    # API Client
│   │   └── store/       # State Management
│   ├── Dockerfile
│   └── package.json
├── nginx/               # Reverse Proxy
├── database/            # Migrations
└── docker-compose.yml
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/products` | GET | List products with dynamic pricing |
| `/api/v1/products/{id}` | GET | Product detail with real-time stock |
| `/api/v1/cart` | GET/POST | Shopping cart operations |
| `/api/v1/checkout` | POST | Create order & initialize payment |
| `/api/v1/orders` | GET | Order history |
| `/api/v1/track/{id}` | GET | Shipment tracking |

## Environment Variables

See `backend/.env.example` for full list. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `PAYMOB_API_KEY`: Paymob payment gateway key
- `BOSTA_API_KEY`: Bosta shipping API key
- `TWILIO_SID`: Twilio account SID
- `ALIEXPRESS_APP_KEY`: AliExpress API credentials

## Architecture

See `docs/ARCHITECTURE.md` for detailed system design, database schema, and scaling strategies.

## Security

- All PII encrypted with Fernet (AES-128)
- PCI-DSS compliant payment processing
- JWT authentication
- Rate limiting on API endpoints
- CORS protection
- SQL injection prevention via SQLAlchemy ORM

## License

Proprietary - GlobalMart Engineering Team 
