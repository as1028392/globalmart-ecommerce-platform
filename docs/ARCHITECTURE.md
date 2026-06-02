# GlobalMart E-Commerce Platform - Technical Architecture

## System Overview

GlobalMart is a cross-border e-commerce platform connecting Egyptian consumers with global suppliers (Turkey, Korea, China) through a unified interface with local payment and delivery.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Mobile App (Flutter/React Native)  │  Web Store (React.js)     │
│  - iOS & Android                    │  - SEO Optimized            │
│  - Unified Codebase                 │  - Responsive Design        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Nginx)                         │
│  - SSL Termination                                               │
│  - Rate Limiting                                                 │
│  - Load Balancing                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI/Django)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Product API │  │  Order API   │  │  Payment API │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │Pricing Engine│  │  Sync Engine │  │Notification  │        │
│  │(Core Logic)  │  │(Suppliers)   │  │Service       │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (Primary)  │  Redis (Cache)  │  S3 (Images/Files)  │
│  - Encrypted User Data │  - Sessions     │  - Product Images   │
│  - Order History       │  - Rate Limits  │  - Invoices         │
│  - Audit Logs          │  - Cart Data    │  - Static Assets    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                          │
├─────────────────────────────────────────────────────────────────┤
│  SUPPLIERS          │  PAYMENT          │  SHIPPING             │
│  - AliExpress API   │  - Paymob         │  - Bosta (Egypt)      │
│  - Turkish Textile  │  - Fawry          │  - Aramex (Intl)      │
│  - Korean Beauty    │  - PayTabs        │                       │
├─────────────────────────────────────────────────────────────────┤
│  COMMUNICATIONS                                                  │
│  - Twilio (SMS)     │  - Firebase (Push)│  - Email (SendGrid)   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Dynamic Pricing Engine
**Location:** `backend/app/services/pricing.py`

The pricing engine is the core trade secret. It calculates real-time EGP prices using:

```
Final_Price_EGP = (Product_Price_USD × Currency_Rate) + 
                  International_Shipping + 
                  Custom_Duties + 
                  Platform_Margin
```

**Features:**
- Real-time USD/EGP exchange rate from Central Bank of Egypt
- Weight-based international shipping calculation
- Configurable customs duties percentage
- Configurable platform margin percentage
- Full price transparency for customer trust
- Sub-100ms calculation time

### 2. Supplier API Integration Hub
**Location:** `backend/app/integrations/suppliers.py`

Handles real-time product synchronization from multiple global sources:

| Supplier | API Type | Authentication | Sync Interval |
|----------|----------|----------------|---------------|
| AliExpress | REST API | HMAC-SHA256 | 30 minutes |
| Turkish Textile | Custom REST | API Key | 30 minutes |
| Korean Beauty | Custom REST | API Key | 30 minutes |

**Features:**
- Automatic product import with image synchronization
- Real-time stock verification before order
- Variant mapping (color, size)
- Weight estimation for shipping calculations

### 3. Payment Gateway Integration
**Location:** `backend/app/integrations/payments.py`

| Method | Gateway | Features |
|--------|---------|----------|
| Vodafone Cash | Paymob | Wallet payment, instant confirmation |
| Meeza Card | Fawry | Local debit card support |
| Visa/Mastercard | Paymob | International card processing |

**Security:**
- PCI-DSS compliant tokenization
- Encrypted transaction data
- Automatic payment status verification
- Refund capability

### 4. Shipping & Logistics
**Location:** `backend/app/integrations/shipping.py`

**Two-stage delivery:**
1. **International:** Aramex (supplier country → Egypt)
2. **Domestic:** Bosta (customs → customer door)

**Features:**
- Automatic waybill generation
- Real-time tracking updates
- SMS notifications at each stage
- Customs clearance integration

### 5. Notification System
**Location:** `backend/app/integrations/notifications.py`

| Channel | Provider | Use Case |
|---------|----------|----------|
| SMS | Twilio | Order confirmations, OTP, status updates |
| Push | Firebase | Real-time order status, promotions |
| Email | SendGrid | Invoices, receipts, marketing |

## Database Schema

### Key Tables

**users**
- Encrypted phone numbers and addresses
- ID numbers for customs clearance
- Verification status

**products**
- Supplier price in USD
- Real-time stock tracking
- Variant JSON storage
- Image URL arrays

**orders**
- Complete price breakdown (subtotal, shipping, duties, margin)
- Encrypted shipping addresses
- Payment transaction references
- Tracking information

**audit_logs**
- GDPR compliance
- Data change tracking
- User action history

## Security Measures

1. **Data Encryption**
   - Fernet symmetric encryption for PII
   - AES-256 for sensitive fields
   - Encrypted at rest and in transit

2. **API Security**
   - JWT authentication
   - Rate limiting (100 req/min)
   - CORS restrictions
   - Input validation

3. **Payment Security**
   - PCI-DSS compliant gateways
   - Token-based transactions
   - No card data storage

4. **Infrastructure**
   - SSL/TLS everywhere
   - DDoS protection
   - WAF (Web Application Firewall)
   - Regular security audits

## Deployment Architecture

### Production Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/globalmart
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=globalmart
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  web:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - web

volumes:
  postgres_data:
  redis_data:
```

### Environment Variables

Create `.env` file from `.env.example` and configure:

```bash
# Required for all deployments
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Payment Gateways
PAYMOB_API_KEY=...
PAYMOB_INTEGRATION_ID=...
FAWRY_MERCHANT_CODE=...

# Shipping
BOSTA_API_KEY=...
ARAMEX_API_KEY=...

# Communications
TWILIO_SID=...
TWILIO_TOKEN=...
FIREBASE_CREDENTIALS_PATH=...

# Suppliers
ALIEXPRESS_APP_KEY=...
ALIEXPRESS_APP_SECRET=...
```

## Scaling Considerations

### Horizontal Scaling
- API servers behind load balancer
- Read replicas for PostgreSQL
- Redis Cluster for sessions/cache
- CDN for static assets and images

### Performance Optimization
- Database indexing on product_id, category
- Redis caching for product listings
- CDN for product images
- Lazy loading for mobile

### Monitoring
- Application: Prometheus + Grafana
- Logs: ELK Stack (Elasticsearch, Logstash, Kibana)
- Errors: Sentry
- Uptime: UptimeRobot

## Development Workflow

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/globalmart.git
cd globalmart

# 2. Start infrastructure
docker-compose up -d db redis

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with local values
uvicorn app.main:app --reload

# 4. Setup frontend
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/
```

## API Documentation

Interactive API docs available at `/docs` when running the backend.

Key endpoints:
- `GET /api/v1/products` - List products with dynamic pricing
- `GET /api/v1/products/{id}` - Product detail with real-time stock
- `POST /api/v1/cart/add` - Add to cart
- `POST /api/v1/checkout` - Create order and initialize payment
- `GET /api/v1/orders` - Order history
- `GET /api/v1/track/{tracking_number}` - Track shipment

## Compliance

- **GDPR:** Encrypted user data, right to deletion, audit logs
- **PCI-DSS:** Tokenized payments, no card storage
- **Egyptian Tax:** VAT calculation, invoice generation
- **Customs:** Accurate duty calculations, proper documentation

## Support & Maintenance

### Regular Tasks
- Daily: Currency rate updates
- Every 30 min: Product sync from suppliers
- Weekly: Security patches
- Monthly: Performance review

### Backup Strategy
- PostgreSQL: Daily automated backups
- Redis: Persistent snapshots
- Files: S3 versioning

---

**Version:** 1.0.0
**Last Updated:** 2024
**Maintainer:** GlobalMart Engineering Team
