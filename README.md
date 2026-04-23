# Django Clean Architecture

A Django REST API built with clean architecture principles, developed phase by phase. Includes a Streamlit UI frontend.

---

## Architecture Overview

```
Request → urls.py → views.py → services.py → repository.py → Database
                                                ↑
                                            models.py
                         ↓
                    serializers.py → Response
```

Each layer has a single responsibility:

| Layer | Responsibility |
|---|---|
| `models.py` | Domain object shape and business rules |
| `repository.py` | Database read/write (MongoDB only) |
| `services.py` | Use cases and business logic |
| `serializers.py` | Input validation and JSON conversion |
| `views.py` | HTTP request/response handling |
| `urls.py` | URL routing |

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend framework | Django 5.1 + Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Message broker | Apache Kafka |
| Document store | MongoDB (notifications) |
| Authentication | JWT (PyJWT) — access + refresh tokens |
| API docs | Swagger UI (drf-spectacular) |
| UI | Streamlit |

---

## Project Structure

```
django-cleanarch/
├── apps/
│   ├── auth/               # JWT login, refresh, logout
│   ├── users/              # User management
│   ├── products/           # Product catalog
│   ├── orders/             # Order lifecycle
│   └── notifications/      # MongoDB-backed notifications
├── config/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Local development
│   │   ├── staging.py      # Staging environment
│   │   ├── production.py   # Production environment
│   │   └── test.py         # Test (SQLite in-memory)
│   ├── urls.py
│   └── exceptions.py       # Global exception handler
├── infrastructure/
│   ├── authentication.py   # JWTAuthentication + IsJWTAuthenticated
│   ├── jwt_utils.py        # Token generation and validation
│   ├── messaging.py        # Kafka producer (fire-and-forget)
│   ├── consumers.py        # Kafka consumer → writes notifications
│   └── mongo.py            # MongoDB connection singleton
├── tests/                  # Unit tests (49 tests)
├── ui/                     # Streamlit frontend
│   ├── app.py              # Login page
│   ├── auth_guard.py       # Auth check for all pages
│   ├── api/client.py       # HTTP client with JWT auto-refresh
│   └── pages/
│       ├── 1_Dashboard.py
│       ├── 2_Products.py
│       ├── 3_Users.py
│       ├── 4_Orders.py
│       └── 5_Notifications.py
├── manage.py
├── requirements.txt
└── pytest.ini
```

---

## Prerequisites

| Service | Version | Default address |
|---|---|---|
| Python | 3.13+ | — |
| PostgreSQL | 16+ | `localhost:5432` |
| Redis | 7+ | `localhost:6379` |
| MongoDB | 7+ | `localhost:27017` |
| Apache Kafka | 3.7+ *(optional)* | `localhost:9092` |

### Start services with Docker

```bash
docker run -d --name pg    -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=cleanarch_db -p 5432:5432 postgres:16
docker run -d --name redis -p 6379:6379 redis:7
docker run -d --name mongo -p 27017:27017 mongo:7
docker run -d --name kafka -p 9092:9092 apache/kafka:3.7.0
```

---

## Installation

```bash
# Clone the repository
git clone git@github.com:phanquocvietspkt1992/Django-ClearnArch.git
cd Django-ClearnArch

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Copy the development env file and adjust values if needed:

```bash
cp .env.development .env
```

`.env.development` defaults:

```env
SECRET_KEY=django-dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=*

DB_NAME=cleanarch_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

MONGO_URL=mongodb://localhost:27017
MONGO_DB=cleanarch_notifications_dev

KAFKA_SERVERS=localhost:9092
```

---

## Running the Project

### 1. Apply migrations

```bash
python manage.py migrate
```

### 2. Start the API server

```bash
python manage.py runserver
```

API available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/api/docs/`

### 3. Start the Streamlit UI

```bash
cd ui
streamlit run app.py
```

UI available at: `http://localhost:8501`

### 4. Start the Kafka consumer *(optional)*

Consumes `order-created` and `product-created` events and writes them to MongoDB as notifications.

```bash
python -m infrastructure.consumers
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/api/auth/login/` | Login — returns access + refresh tokens | ❌ |
| POST | `/api/auth/refresh/` | Refresh access token | ❌ |
| POST | `/api/auth/logout/` | Revoke refresh token | ❌ |

### Users
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/api/users/` | List all users | ❌ |
| POST | `/api/users/` | Register new user | ❌ |
| GET | `/api/users/<id>/` | Get user by ID | ❌ |
| PUT | `/api/users/<id>/` | Update user profile | ❌ |
| POST | `/api/users/<id>/deactivate/` | Deactivate user | ❌ |

### Products
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/api/products/` | List all products | ❌ |
| POST | `/api/products/` | Create product | ❌ |
| GET | `/api/products/<id>/` | Get product by ID | ❌ |
| PUT | `/api/products/<id>/` | Update product | ❌ |
| DELETE | `/api/products/<id>/` | Delete product | ❌ |

### Orders
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/api/orders/?user_id=<id>` | List orders by user | ✅ |
| POST | `/api/orders/` | Place new order | ✅ |
| GET | `/api/orders/<id>/` | Get order detail | ✅ |
| PATCH | `/api/orders/<id>/status/` | Update order status | ✅ |

#### Order status transitions
```
pending → confirmed → shipped → delivered
any (except delivered/cancelled) → cancelled
```

PATCH body: `{ "action": "confirm" | "ship" | "deliver" | "cancel" }`

### Notifications
| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/api/notifications/?user_id=<id>` | List notifications for user | ❌ |
| PATCH | `/api/notifications/<id>/read/` | Mark notification as read | ❌ |
| PATCH | `/api/notifications/read-all/` | Mark all as read for user | ❌ |

---

## Authentication

The API uses JWT authentication with short-lived access tokens and long-lived refresh tokens.

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# Response
# { "access_token": "...", "refresh_token": "..." }

# 2. Use access token on protected endpoints
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>"

# 3. Refresh when access token expires
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

| Token | Lifetime | Storage |
|---|---|---|
| Access token | 15 minutes | Memory |
| Refresh token | 7 days | Redis |

---

## Running Tests

Tests use SQLite in-memory and local memory cache — no external services needed.

```bash
pytest
```

```
49 passed in 0.2s
```

---

## Environment Settings

| Environment | Command | Use case |
|---|---|---|
| Development | `python manage.py runserver` | Local development |
| Staging | `DJANGO_SETTINGS_MODULE=config.settings.staging gunicorn config.wsgi` | QA / pre-production |
| Production | `DJANGO_SETTINGS_MODULE=config.settings.production gunicorn config.wsgi` | Live server |

Key differences:

| Setting | Development | Staging | Production |
|---|---|---|---|
| DEBUG | ✅ | ❌ | ❌ |
| Swagger UI | ✅ | ✅ | 🔒 auth required |
| HTTPS redirect | ❌ | ❌ | ✅ |
| HSTS | ❌ | ❌ | ✅ 1 year |
| Log level | DEBUG | INFO | ERROR |
