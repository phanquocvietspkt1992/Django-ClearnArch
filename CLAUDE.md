# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests (no external services needed)
pytest

# Run a single test file
pytest tests/test_orders.py

# Run a single test
pytest tests/test_orders.py::TestOrderListView::test_create_order_returns_201

# Start API server (defaults to development settings)
python manage.py runserver

# Start API server for a specific environment
DJANGO_SETTINGS_MODULE=config.settings.staging python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations after model changes
DJANGO_ENV=development python manage.py makemigrations <app_name>

# Start Streamlit UI
cd ui && streamlit run app.py

# Start Kafka consumer (writes events to MongoDB as notifications)
python -m infrastructure.consumers
```

## Settings and Environment

Settings are split by environment under `config/settings/`:
- `base.py` — shared settings; reads `SECRET_KEY` from env (no default — will raise if missing)
- `development.py` — DEBUG=True, CORS open, SQL query logging
- `staging.py` — DEBUG=False, security cookies, INFO logging
- `production.py` — HTTPS enforced, HSTS, ERROR logging only
- `test.py` — SQLite in-memory, local memory cache, hardcoded SECRET_KEY

`base.py` auto-loads `.env.<DJANGO_ENV>` (e.g. `.env.development`) based on the `DJANGO_ENV` env var, falling back to `.env`. `manage.py` defaults to `config.settings.development`.

`pytest.ini` sets `DJANGO_SETTINGS_MODULE=config.settings.test` — tests never need external services.

## Architecture

Each app follows the same layered pattern:

```
urls.py → views.py → services.py → (repository.py) → models.py
                ↓
          serializers.py
```

- **models.py** — domain object with business rules as methods (e.g. `order.cancel()`, `user.deactivate()`). Django ORM models for SQL apps; plain Python classes for MongoDB (notifications).
- **services.py** — use cases; only layer that enforces business rules across objects. Never touches HTTP or the database directly.
- **repository.py** — exists only in `notifications/`; all MongoDB access is isolated here. SQL apps use the ORM directly in services.
- **serializers.py** — input validation (create/update) and output formatting. Uses `serializers.ModelSerializer` for SQL models and `serializers.Serializer` for plain Python objects.
- **views.py** — thin HTTP layer; delegates entirely to services. No business logic here.
- **exceptions.py** — `DomainException` (→ 400) and `NotFoundException` (→ 404) live in `apps/users/exceptions.py` and are re-exported from other apps. The global handler is in `config/exceptions.py`.

## Infrastructure Layer

`infrastructure/` contains cross-cutting concerns shared across apps:

- **`authentication.py`** — `JWTAuthentication` (DRF `BaseAuthentication`) parses `Bearer` tokens. Returns `AuthenticatedUser(user_id)` as `request.user`. `IsJWTAuthenticated` permission checks `isinstance(request.user, AuthenticatedUser)`. Apply both to views that need protection.
- **`jwt_utils.py`** — access tokens (HS256, 15 min); refresh tokens (UUID stored in Redis, 7 days). `rotate_refresh_token` invalidates the old token and issues a new one.
- **`messaging.py`** — Kafka producer, fire-and-forget. Wraps `confluent_kafka.Producer`. Never raises — failures are silently swallowed so they don't block API responses.
- **`consumers.py`** — standalone Kafka consumer; run as a separate process. Calls `apps.notifications.services` to write MongoDB documents.
- **`mongo.py`** — lazy singleton returning a `pymongo` database handle.

## Adding a New App

Follow the pattern of any existing app:

1. Create `apps/<name>/` with `__init__.py`, `models.py`, `serializers.py`, `services.py`, `views.py`, `urls.py`, `exceptions.py`
2. Add `'apps.<name>'` to `INSTALLED_APPS` in `config/settings/base.py`
3. Add `path('api/', include('apps.<name>.urls'))` in `config/urls.py`
4. Run `makemigrations` if the app has Django ORM models
5. Add tests in `tests/test_<name>.py`

## Testing Conventions

All tests use `APIRequestFactory` and mock the service layer with `unittest.mock.patch`. Tests never hit real services.

For views protected by `JWTAuthentication`, patch the authenticate method in `setup_method` / `teardown_method`:

```python
from infrastructure.authentication import AuthenticatedUser

class TestProtectedView:
    def setup_method(self):
        self._p = patch('infrastructure.authentication.JWTAuthentication.authenticate',
                        return_value=(AuthenticatedUser('user-id'), 'token'))
        self._p.start()

    def teardown_method(self):
        self._p.stop()
```

## Notifications App (MongoDB)

`apps/notifications/` is different from other apps — it uses MongoDB instead of PostgreSQL:
- `models.py` is a plain Python class (no Django ORM), with `to_doc()` / `from_doc()` for MongoDB serialization
- `repository.py` is the only file that calls `get_db()` — all MongoDB queries live here
- No Django migrations for this app
- Notifications are created by the Kafka consumer (`infrastructure/consumers.py`), not by API clients
