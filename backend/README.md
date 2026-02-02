# Warehouse Scale Automation - Backend

Flask-based REST API for warehouse inventory management with staging/approval workflow.

## Quick Start

```bash
cd backend
source venv/bin/activate
python run.py  # Starts on http://localhost:5001
```

## API Documentation

- **Swagger UI**: http://localhost:5001/swagger-ui
- **OpenAPI JSON**: http://localhost:5001/openapi.json

## Authentication

All `/api/*` endpoints require Bearer token:
```
Authorization: Bearer <API_TOKEN>
```

Set `API_TOKEN` in your `.env` file.

---

## API Endpoints

### Health (Public)
```bash
curl http://localhost:5001/health
```

### Articles

**List articles:**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
  http://localhost:5001/api/articles
```

**Create article:**
```bash
curl -X POST \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"article_no": "ART-001", "description": "Blue Paint", "is_paint": true}' \
  http://localhost:5001/api/articles
```

**Get article by article_no:**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
  http://localhost:5001/api/articles/ART-001
```

### Batches

**List batches for article:**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
  http://localhost:5001/api/articles/ART-001/batches
```

**Create batch:**
```bash
curl -X POST \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"article_id": 1, "batch_code": "0044"}' \
  http://localhost:5001/api/batches
```

### Drafts

**List drafts (filter by status):**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
  "http://localhost:5001/api/drafts?status=DRAFT"
```

**Create draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "article_id": 1,
    "batch_id": 1,
    "quantity_kg": 5.25,
    "client_event_id": "uuid-12345-abcde"
  }' \
  http://localhost:5001/api/drafts
```

**Update draft:**
```bash
curl -X PATCH \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"quantity_kg": 6.50, "note": "Updated weight"}' \
  http://localhost:5001/api/drafts/1
```

### Approvals

**Approve draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"actor_user_id": 1, "note": "Approved by admin"}' \
  http://localhost:5001/api/drafts/1/approve
```

**Reject draft:**
```bash
curl -X POST \
  -H "Authorization: Bearer dev-secret-token-123" \
  -H "Content-Type: application/json" \
  -d '{"actor_user_id": 1, "note": "Incorrect quantity"}' \
  http://localhost:5001/api/drafts/1/reject
```

### Reports (Stubs - 501)

**Inventory report:**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
  http://localhost:5001/api/reports/inventory
```

**Transaction report:**
```bash
curl -H "Authorization: Bearer dev-secret-token-123" \
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
| 409 | Conflict (duplicate, wrong status) |
| 500 | Internal server error |
| 501 | Not implemented (stubs) |

## Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | - | PostgreSQL connection string |
| APP_HOST | 127.0.0.1 | Server host |
| APP_PORT | 5001 | Server port |
| ENV | development | Environment mode |
| API_TOKEN | - | Bearer token for auth |

## CLI Commands

```bash
flask seed        # Create location "13" + users
flask db upgrade  # Apply migrations
flask db migrate  # Create new migration
```
