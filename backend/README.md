# Warehouse Scale Automation - Backend

Flask-based REST API for warehouse inventory management with JWT authentication and role-based access control.

## Dev Setup Checklist

```bash
# 1. Clone and setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create database
createdb warehouse  # or via pgAdmin/DBeaver

# 3. Configure environment
cp .env.example .env
# Edit .env with:
#   DATABASE_URL=postgresql+psycopg2://localhost:5432/warehouse
#   JWT_SECRET_KEY=your-very-long-random-secret-key

# 4. Run migrations
flask db upgrade

# 5. Seed initial data with users
flask seed                  # Creates location + users with passwords
flask seed --demo           # Also adds sample articles/batches/inventory

# 6. Start server
python run.py               # Runs on http://localhost:5001

# 7. Verify
curl http://localhost:5001/health
```

---

## Authentication (JWT)

All `/api/*` endpoints (except `/api/auth/login`) require JWT Bearer token.

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| stefan | ChangeMe123! | ADMIN |
| operator | Operator123! | OPERATOR |

> ⚠️ **CHANGE THESE PASSWORDS IMMEDIATELY** after first login!

### Login Flow

```bash
# 1. Login to get tokens
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "stefan", "password": "ChangeMe123!"}'

# Response:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "user": {"id": 1, "username": "stefan", "role": "ADMIN"}
# }

# 2. Use access_token for API calls
export TOKEN="eyJ..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:5001/api/articles

# 3. Refresh when access_token expires (15 min default)
curl -X POST http://localhost:5001/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"
```

### Token Expiration

| Token | Default Expiry | Env Var |
|-------|----------------|---------|
| Access | 15 minutes | JWT_ACCESS_EXPIRES_MINUTES |
| Refresh | 30 days | JWT_REFRESH_EXPIRES_DAYS |

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **ADMIN** | All operations: approve/reject drafts, create articles/batches, inventory adjustments |
| **OPERATOR** | Create drafts, view drafts/articles/batches/reports |

---

## Batch Code Validation Rules

Valid batch codes are **numeric only**:

| Format | Length | Examples | Manufacturer |
|--------|--------|----------|--------------|
| Short | 4-5 digits | 0044, 1045, 10455 | Mankiewicz |
| Long | 9-12 digits | 292456953, 2924662112, 292466211255 | Akzo Nobel |

---

## Transaction Quantity Convention v1

| Transaction Type | Quantity Sign | Description |
|------------------|---------------|-------------|
| `WEIGH_IN` | **Positive** | Amount weighed/recorded |
| `SURPLUS_CONSUMED` | **Negative** | Decrease in surplus |
| `STOCK_CONSUMED` | **Negative** | Decrease in stock |
| `INVENTORY_ADJUSTMENT` | **+/-** | Delta (new - old) |

---

## Inventory Count (Admin)

Admin can perform inventory count via `POST /api/inventory/count`.
- **Over**: Excess quantity added to Surplus.
- **Under**: Surplus reset to 0; remaining deficit creates `INVENTORY_SHORTAGE` draft.
- **Drafts**: Shortage drafts consume **Stock only** upon approval.

## Common Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `ALIAS_LIMIT_REACHED` | 409 | Max 5 aliases per article allowed |
| `ALIAS_NOT_FOUND` | 404 | Alias ID not found |
| `DUPLICATE_ALIAS` | 409 | Alias already exists globally |
| `INVALID_EXPIRY_DATE` | 400 | Expiry date required/invalid |
| `INVENTORY_COUNT_INVALID` | 400 | Invalid count payload |
| `INSUFFICIENT_STOCK` | 409 | Not enough stock for approval |
| `DRAFT_NOT_DRAFT` | 400 | Draft not in DRAFT status |

---

## Running Tests

```bash
createdb warehouse_test
pytest tests/ -v
```

---

## API Documentation

- **Swagger UI**: http://localhost:5001/swagger-ui
- **OpenAPI JSON**: http://localhost:5001/openapi.json

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | localhost/warehouse | PostgreSQL connection |
| JWT_SECRET_KEY | dev-secret-... | **REQUIRED in production** |
| JWT_ACCESS_EXPIRES_MINUTES | 15 | Access token lifetime |
| JWT_REFRESH_EXPIRES_DAYS | 30 | Refresh token lifetime |
| APP_HOST | 127.0.0.1 | Server host |
| APP_PORT | 5001 | Server port |
| ENV | development | Environment |

## CLI Commands

```bash
flask seed            # Create location + users with passwords
flask seed --demo     # Also add sample inventory
flask db upgrade      # Apply migrations
flask db migrate -m "msg"  # Create migration
```
