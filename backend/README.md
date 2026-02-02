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

## API Documentation

- **Swagger UI**: http://localhost:5001/swagger-ui
- **OpenAPI JSON**: http://localhost:5001/openapi.json

## Authentication

All `/api/*` endpoints require Bearer token:
```
Authorization: Bearer <API_TOKEN>
```

Set `API_TOKEN` in your `.env` file.

### Security Behavior

| ENV | API_TOKEN | ALLOW_NO_AUTH_IN_DEV | Behavior |
|-----|-----------|----------------------|----------|
| production | empty | - | **Startup error** |
| production | set | - | Token required |
| development | empty | false | Token required (warn) |
| development | empty | true | No auth needed (dev only) |
| development | set | - | Token required |

---

## Transaction Quantity Convention v1

Transaction records are the **audit trail** for inventory changes. Actual inventory levels come from `stock` and `surplus` tables.

| Transaction Type | Quantity Sign | Description |
|------------------|---------------|-------------|
| `WEIGH_IN` | **Positive** | Amount weighed/recorded from scale |
| `SURPLUS_CONSUMED` | **Negative** | Decrease in surplus inventory |
| `STOCK_CONSUMED` | **Negative** | Decrease in stock inventory |
| `INVENTORY_ADJUSTMENT` | **+/-** | Manual corrections (future) |

**Example**: Approving a 10kg draft with 3kg surplus and 7kg from stock creates:
- `WEIGH_IN: +10.00kg`
- `SURPLUS_CONSUMED: -3.00kg`
- `STOCK_CONSUMED: -7.00kg`

---

## API Endpoints

### Health (Public)
```bash
curl http://localhost:5001/health
```

### Articles

**List articles:**
```bash
curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:5001/api/articles
```

**Create article:**
```bash
curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"article_no": "ART-001", "description": "Blue Paint", "is_paint": true}' \
  http://localhost:5001/api/articles
```

### Batches

**List batches for article:**
```bash
curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:5001/api/articles/ART-001/batches
```

**Create batch:**
```bash
curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"article_id": 1, "batch_code": "0044"}' \
  http://localhost:5001/api/batches
```

### Drafts

**List drafts:**
```bash
curl -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:5001/api/drafts?status=DRAFT"
```

**Create draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "article_id": 1,
    "batch_id": 1,
    "quantity_kg": 5.25,
    "client_event_id": "uuid-12345"
  }' \
  http://localhost:5001/api/drafts
```

### Approvals

**Approve draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"actor_user_id": 1, "note": "Approved"}' \
  http://localhost:5001/api/drafts/1/approve
```

**Reject draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"actor_user_id": 1, "note": "Incorrect quantity"}' \
  http://localhost:5001/api/drafts/1/reject
```

### Reports

```bash
curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:5001/api/reports/inventory

curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:5001/api/reports/transactions
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
| 409 | Conflict (duplicate, wrong status, insufficient stock) |
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

## CLI Commands

```bash
flask seed            # Create location + users
flask seed --demo     # Also add sample inventory
flask db upgrade      # Apply migrations
flask db migrate -m "msg"  # Create migration
```
