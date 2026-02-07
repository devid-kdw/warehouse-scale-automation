# Warehouse Scale Automation - Project Specification v2.1

## 0. Overview

Internal warehouse system for paint inventory (later: consumables) with emphasis on:
- **Consumption tracking** by article + batch + location
- **Staging/approval workflow**: nothing changes stock until admin approves
- **Audit trail** and reports (exportable to Excel/SAP template)

### Core v2.1 Scope (Software-first, no hardware)
- **Draft Groups**: Atomic multi-line approval.
- **Stock Receiving**: Inbound workflow with order numbers.
- **Consumables**: System batch logic.
- **Security**: JWT Auth + Electron Hardening.

| Domain | Tables |
|--------|--------|
| Master Data | `articles`, `batches`, `locations` |
| Inventory | `stock`, `surplus` |
| Staging | `weigh_in_drafts`, `draft_groups` |
| Approval | `approval_actions` |
| Audit | `transactions` |
| Users | `users` (RBAC: Admin/Operator) |

> [!NOTE]
> Hardware integration (scale, barcode) is **NOT** in v2.1. UI uses manual input; hardware plugs in later as alternative input source.

---

## 1. Deployment & Dev Workflow

| Environment | Host | Components |
|-------------|------|------------|
| **Dev** | macOS | Backend + PostgreSQL locally, UI locally |
| **Test** | Ubuntu laptop | Remote client hitting Mac backend |
| **Prod** | Raspberry Pi | Backend + PostgreSQL |

- **Backend port**: `5001` (default)
- **Database**: PostgreSQL from day one
- **Config**: Environment variables only (`.env`), nothing hardcoded

---

## 2. Repository Structure

```
warehouse-scale-automation/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── error_handling.py
│   │   ├── auth.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── articles.py
│   │   │   ├── batches.py
│   │   │   ├── drafts.py
│   │   │   ├── approvals.py
│   │   │   └── reports.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── articles.py
│   │   │   ├── batches.py
│   │   │   ├── drafts.py
│   │   │   ├── approvals.py
│   │   │   └── reports.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── location.py
│   │   │   ├── article.py
│   │   │   ├── batch.py
│   │   │   ├── stock.py
│   │   │   ├── surplus.py
│   │   │   ├── weigh_in_draft.py
│   │   │   ├── approval_action.py
│   │   │   └── transaction.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── approval_service.py
│   │   │   └── validation.py
│   │   └── cli/
│   │       ├── __init__.py
│   │       └── seed.py
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   ├── run.py
│   ├── .env.example
│   └── README.md
├── desktop-ui/
│   └── (Electron + React — later)
├── docs/
├── .gitignore
└── README.md
```

---

## 3. Environment Variables

### Backend (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | `postgresql+psycopg2://user:pass@localhost:5432/warehouse` |
| `APP_HOST` | `127.0.0.1` | Use `0.0.0.0` for LAN access |
| `APP_PORT` | `5001` | Backend port |
| `ENV` | `development` | Environment mode |
| `API_TOKEN` | - | Shared secret for write endpoints |

### Desktop UI

| Variable | Description |
|----------|-------------|
| `BACKEND_BASE_URL` | Backend URL (e.g., `http://localhost:5001`) |
| `API_TOKEN` | Shared secret |

---

## 4. Security & Access Policy

| Endpoint | Auth Required |
|----------|---------------|
| `GET /health` | ❌ Public |
| `POST /api/auth/login` | ❌ Public (Rate Limited) |
| All other endpoints | ✅ Bearer token (JWT) |

**Auth header format:**
```
Authorization: Bearer <access_token>
```

> [!IMPORTANT]
> **JWT Implementation**:
> - Access Token: 15 minutes
> - Refresh Token: 7 days
> - RBAC: Enforced via `@require_roles` decorator.
> - Electron: `nodeIntegration: false` for security.

---

## 5. Timezone & Timestamps

- All DB timestamps: **UTC** (`TIMESTAMP WITH TIME ZONE`)
- UI may display local time
- Backend always stores UTC

---

## 6. Quantity Policy

| Property | Value |
|----------|-------|
| Unit | kg |
| Precision | 2 decimals |
| Min | 0.01 |
| Max (v1.1) | 9999.99 (configurable) |
| Rounding | HALF_UP |
| DB type | `NUMERIC(14,2)` |

---

## 7. Batch Code Policy

Batch codes are numeric strings:

| Supplier | Format | Example |
|----------|--------|---------|
| Mankiewicz | 4 digits | `0044`, `1045`, `0667` |
| Akzo | 9-10 digits | `292456953`, `2924662112` |

**Validation regex:** `^\d{4}$|^\d{9,10}$`

---

## 8. Idempotency Policy

- `client_event_id` is **REQUIRED** on create draft endpoint
- UI generates UUID automatically (invisible to user)
- **Unique constraint** on `weigh_in_drafts.client_event_id`

---

## 9. Concurrency Policy (Approval)

Approval must be **atomic**:

```sql
-- 1. Lock draft
SELECT * FROM weigh_in_drafts WHERE id = ? FOR UPDATE;

-- 2. Verify status = 'DRAFT'

-- 3. Lock stock/surplus rows
SELECT * FROM surplus WHERE ... FOR UPDATE;
SELECT * FROM stock WHERE ... FOR UPDATE;

-- 4. Update in same transaction
UPDATE weigh_in_drafts SET status = 'APPROVED' WHERE id = ?;
-- Update stock/surplus quantities
-- Insert transaction record
```

---

## 10. Database Schema

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| username | TEXT | UNIQUE NOT NULL |
| role | TEXT | NOT NULL (`ADMIN`, `OPERATOR`) |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### `locations`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| code | TEXT | UNIQUE NOT NULL |
| name | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### `articles`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| article_no | TEXT | UNIQUE NOT NULL |
| description | TEXT | NULLABLE |
| article_group | TEXT | NULLABLE |
| base_uom | TEXT | NOT NULL DEFAULT 'kg' |
| pack_size | NUMERIC(12,3) | NULLABLE |
| pack_uom | TEXT | NULLABLE |
| barcode | TEXT | NULLABLE |
| is_paint | BOOLEAN | DEFAULT TRUE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |

### `batches`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| article_id | INTEGER | FK → articles.id NOT NULL |
| batch_code | TEXT | NOT NULL |
| received_date | DATE | NULLABLE |
| expiry_date | DATE | NULLABLE |
| note | TEXT | NULLABLE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| | | UNIQUE(article_id, batch_code) |

### `stock`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| location_id | INTEGER | FK → locations.id NOT NULL |
| article_id | INTEGER | FK → articles.id NOT NULL |
| batch_id | INTEGER | FK → batches.id NOT NULL |
| quantity_kg | NUMERIC(14,2) | DEFAULT 0, CHECK >= 0 |
| last_updated | TIMESTAMPTZ | DEFAULT NOW() |
| | | UNIQUE(location_id, article_id, batch_id) |

### `surplus`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| location_id | INTEGER | FK → locations.id NOT NULL |
| article_id | INTEGER | FK → articles.id NOT NULL |
| batch_id | INTEGER | FK → batches.id NOT NULL |
| quantity_kg | NUMERIC(14,2) | DEFAULT 0, CHECK >= 0 |
| reason | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() |
| | | UNIQUE(location_id, article_id, batch_id) |

### `weigh_in_drafts`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| location_id | INTEGER | FK → locations.id NOT NULL |
| article_id | INTEGER | FK → articles.id NOT NULL |
| batch_id | INTEGER | FK → batches.id NOT NULL |
| quantity_kg | NUMERIC(14,2) | CHECK (0 < qty <= 9999.99) |
| status | TEXT | DEFAULT 'DRAFT' |
| created_by_user_id | INTEGER | FK → users.id NULLABLE |
| source | TEXT | DEFAULT 'manual' |
| client_event_id | TEXT | NOT NULL UNIQUE |
| note | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

**Status values:** `DRAFT`, `APPROVED`, `REJECTED`

### `approval_actions`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| draft_id | INTEGER | FK → weigh_in_drafts.id NOT NULL |
| action | TEXT | NOT NULL (`APPROVE`, `REJECT`, `EDIT`) |
| actor_user_id | INTEGER | FK → users.id NOT NULL |
| old_value | JSONB | NULLABLE |
| new_value | JSONB | NULLABLE |
| note | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### `transactions`
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| tx_type | TEXT | NOT NULL |
| occurred_at | TIMESTAMPTZ | DEFAULT NOW() |
| location_id | INTEGER | FK → locations.id NOT NULL |
| article_id | INTEGER | FK → articles.id NOT NULL |
| batch_id | INTEGER | FK → batches.id NOT NULL |
| quantity_kg | NUMERIC(14,2) | NOT NULL |
| user_id | INTEGER | FK → users.id NULLABLE |
| source | TEXT | DEFAULT 'ui' |
| client_event_id | TEXT | NULLABLE (indexed) |
| meta | JSONB | NULLABLE |

**tx_type values:** `WEIGH_IN`, `SURPLUS_CONSUMED`, `STOCK_CONSUMED`, `INVENTORY_ADJUSTMENT` (future)

**Indexes:**
- `occurred_at`
- `(article_id, occurred_at)`
- `(batch_id, occurred_at)`

---

## 11. Error Handling

All errors return:

```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human readable",
    "details": {}
  }
}
```

### Error Code Table

| Code | HTTP Status |
|------|-------------|
| `INVALID_TOKEN` | 401 |
| `VALIDATION_ERROR` | 400 |
| `DRAFT_NOT_FOUND` | 404 |
| `DRAFT_NOT_DRAFT` | 409 |
| `DUPLICATE_EVENT_ID` | 409 |
| `INVALID_BATCH_FORMAT` | 400 |
| `INSUFFICIENT_STOCK` | 409 |
| `ARTICLE_NOT_FOUND` | 404 |
| `BATCH_NOT_FOUND` | 404 |
| `LOCATION_NOT_FOUND` | 404 |
| `INTERNAL_ERROR` | 500 |

---

## 12. API Documentation

Use **flask-smorest** for:
- Swagger UI at `/swagger-ui`
- OpenAPI JSON at `/openapi.json`
- Marshmallow schemas for request/response validation

---

## 13. Seed Data (CLI)

Provide CLI command `flask seed`:

```bash
flask seed
```

Creates:
1. Location with code `"13"`
2. Admin user `stefan` with role `ADMIN`
3. Operator user `operator` with role `OPERATOR` (optional)

---

## Quick Start Guide

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for desktop UI, later)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
createdb warehouse

# Run migrations
flask db upgrade

# Seed initial data
flask seed

# Start development server
python run.py
```

### Verify Installation

```bash
# Health check (no auth)
curl http://localhost:5001/health

# API docs
open http://localhost:5001/swagger-ui
```

---

## Development Notes

### Adding New Endpoints
1. Create Marshmallow schema in `app/schemas/`
2. Create API blueprint in `app/api/`
3. Register blueprint in `app/api/__init__.py`
4. Add tests in `tests/`

### Database Migrations
```bash
flask db migrate -m "Description"
flask db upgrade
```

### Running Tests
```bash
pytest
pytest --cov=app  # With coverage
```
