# Warehouse Scale Automation - Backend

Flask-based REST API for warehouse inventory management with staging/approval workflow.

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
# Edit .env with your DATABASE_URL and API_TOKEN

# 4. Run migrations
flask db upgrade

# 5. Seed initial data
flask seed                  # Creates location "13" + users
flask seed --demo           # Also adds sample articles/batches/inventory

# 6. Start server
python run.py               # Runs on http://localhost:5001

# 7. Verify
curl http://localhost:5001/health
```

## Running Tests

```bash
# Create test database
createdb warehouse_test

# Run tests (uses default test DB)
pytest tests/ -v

# Or specify custom test DB
export TEST_DATABASE_URL=postgresql+psycopg2://localhost:5432/my_test_db
pytest tests/ -v
```

---

## Batch Code Validation Rules

Valid batch codes are **numeric only** and must match:

| Format | Length | Examples | Manufacturer |
|--------|--------|----------|--------------|
| Short | 4-5 digits | 0044, 1045, 10455 | Mankiewicz |
| Long | 9-12 digits | 292456953, 2924662112, 292466211255 | Akzo Nobel |

**Invalid examples:**
- `123` (too short - 3 digits)
- `123456` (in the gap - 6-8 digits)
- `abc123` (non-numeric)
- `12-34` (contains hyphen)

---

## Transaction Quantity Convention v1

Transaction records are the **audit trail** for inventory changes. Actual inventory levels come from `stock` and `surplus` tables.

| Transaction Type | Quantity Sign | Description |
|------------------|---------------|-------------|
| `WEIGH_IN` | **Positive** | Amount weighed/recorded from scale |
| `SURPLUS_CONSUMED` | **Negative** | Decrease in surplus inventory |
| `STOCK_CONSUMED` | **Negative** | Decrease in stock inventory |
| `INVENTORY_ADJUSTMENT` | **+/-** | Delta (new - old) for audit |

**Example**: Approving a 10kg draft with 3kg surplus and 7kg from stock creates:
- `WEIGH_IN: +10.00kg`
- `SURPLUS_CONSUMED: -3.00kg`
- `STOCK_CONSUMED: -7.00kg`

---

## API Documentation

- **Swagger UI**: http://localhost:5001/swagger-ui
- **OpenAPI JSON**: http://localhost:5001/openapi.json

## Authentication

All `/api/*` endpoints require Bearer token:
```
Authorization: Bearer <API_TOKEN>
```

### Security Behavior

| ENV | API_TOKEN | Behavior |
|-----|-----------|----------|
| production | empty | **Startup error** |
| production | set | Token required |
| development | empty | Token required (ALLOW_NO_AUTH_IN_DEV=true skips) |
| development | set | Token required |

---

## Smoke Test Commands

```bash
# Set token for convenience
export TOKEN="dev-secret-token-123"

# Health check
curl http://localhost:5001/health

# Create article
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"article_no": "TEST-001", "description": "Test Paint"}' \
  http://localhost:5001/api/articles

# Create batch (4-5 digits)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"article_id": 1, "batch_code": "0044"}' \
  http://localhost:5001/api/batches

# Create batch (9-12 digits)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"article_id": 1, "batch_code": "292456953"}' \
  http://localhost:5001/api/batches

# Set stock via inventory adjust
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "article_id": 1,
    "batch_id": 1,
    "target": "stock",
    "mode": "set",
    "quantity_kg": 50.00,
    "actor_user_id": 1,
    "note": "Initial stock"
  }' \
  http://localhost:5001/api/inventory/adjust

# Create draft
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "article_id": 1,
    "batch_id": 1,
    "quantity_kg": 5.25,
    "client_event_id": "test-001"
  }' \
  http://localhost:5001/api/drafts

# Approve draft
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"actor_user_id": 1}' \
  http://localhost:5001/api/drafts/1/approve

# Archive article
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/articles/1/archive

# List archived articles
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5001/api/articles?active=false"

# Restore article
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:5001/api/articles/1/restore
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Invalid/missing token |
| 404 | Resource not found |
| 409 | Conflict (duplicate, wrong status, insufficient stock, article in use) |
| 500 | Internal server error |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | localhost/warehouse | PostgreSQL connection |
| APP_HOST | 127.0.0.1 | Server host |
| APP_PORT | 5001 | Server port |
| ENV | development | Environment (development/production) |
| API_TOKEN | - | Bearer token for auth |
| ALLOW_NO_AUTH_IN_DEV | false | Skip auth in dev when token empty |
| CORS_ORIGINS | localhost:5173,3000 | Allowed CORS origins |
| CORS_ALLOW_ALL | false | Allow all origins (dev only) |
| TEST_DATABASE_URL | localhost/warehouse_test | Test database |

## CLI Commands

```bash
flask seed            # Create location + users
flask seed --demo     # Also add sample inventory
flask db upgrade      # Apply migrations
flask db migrate -m "msg"  # Create migration
```
