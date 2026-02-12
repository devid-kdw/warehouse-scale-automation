# Orchestrator Full Project Review — 2026-02-10

**Reviewer:** Orchestrator  
**Scope:** Full codebase audit (backend + frontend + docs + tests)  
**Goal:** Identify bugs, inconsistencies, and improvements. Delegate fixes via Task Briefs.

---

## 🔴 BUGS — Must Fix

### BUG-1: Duplicate `batch_id` Resolution in `create_group()` (CRITICAL)
**File:** `backend/app/services/draft_group_service.py` lines 66–112  
**Severity:** P0 — Causes redundant DB queries; potential incorrect batch_id overwrite

The `batch_id` resolution logic (checking `is_paint`, calling `batch_service.get_or_create_system_batch`) appears **twice** in the same loop body:
- First at lines 72–81
- Duplicated again at lines 100–112

The second block **overwrites** `batch_id` from the first block because `line_data.get('batch_id')` is called again. This means if a paint article provides a valid `batch_id`, the second block still re-reads it (harmless but wasteful), and for consumables, `get_or_create_system_batch` is called **twice**. The duplicate `article` fetch at line 103 also leaks a second query.

**Fix:** Remove lines 100–112 entirely (the duplicated second block).

---

### BUG-2: `test_shortage_draft.py` Uses Wrong API Path
**File:** `backend/tests/test_shortage_draft.py` lines 41, 66  
**Severity:** P1 — Tests silently passing with wrong assertions

Tests hit `/api/approvals/{id}/approve` but the actual approval endpoint is at `/api/drafts/{id}/approve` (see `approvals.py` `url_prefix='/api/drafts'`). The test was previously "fixed" by setting expected status to 404 — but that means the test **isn't actually testing approval logic**. It's just confirming a 404.

**Fix:** Change test paths to `/api/drafts/{id}/approve` and restore proper assertions (200 for success, 409 for insufficient stock).

---

### BUG-3: `inventory_count` Error Handler References Non-Existent Attributes
**File:** `backend/app/api/inventory.py` line 300  
**Severity:** P1 — Runtime crash on AppError

```python
'code': e.error_code,  # ← AppError has `.code` not `.error_code`
...
}, e.status_code          # ← AppError has no `.status_code` attribute
```

`AppError` defines `self.code` and `self.message` (see `error_handling.py:59`), not `error_code` or `status_code`. This will raise `AttributeError` whenever the inventory count endpoint catches an `AppError`.

**Fix:** Use `e.code` and derive HTTP status from `ERROR_CODES` mapping, or use the global error handler pattern.

---

### BUG-4: Location ID Hardcoded to `1` Everywhere — Must Be `13` (CRITICAL)
**Severity:** P0 — All data is being stored under the wrong location

Per Stefan's confirmation and `RULES_OF_ENGAGEMENT.md` Rule 3, the default Location ID is **13** (location code `'13'`). However, the **entire codebase** hardcodes `location_id=1`:

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `receiving_service.py` | 23 | `location_id: int = 1` | `location_id: int = 13` |
| `receiving_service.py` | 104 | `if location_id != 1` | `if location_id != 13` |
| `api/inventory.py` | 207 | `location_id if location_id else 1` | `location_id if location_id else 13` |
| `api/inventory.py` | 340 | `data.get('location_id', 1)` | `data.get('location_id', 13)` |
| `schemas/inventory.py` | 42 | `load_default=1` | `load_default=13` |
| `schemas/inventory.py` | 90 | `load_default=1` | `load_default=13` |
| `desktop-ui Receiving/index.tsx` | 28 | `location_id: 1` | `location_id: 13` |
| `desktop-ui DraftEntry.tsx` | 42 | `location_id: '1'` | `location_id: '13'` |
| `desktop-ui types.ts` | 175 | `// Defaults to 1` | `// Defaults to 13` |

> [!IMPORTANT]
> The system should keep `location_id` configurable (not remove the field), but the **default** must be `13`.

---

### BUG-5: `console.log` Debug Statements in Production Code
**File:** `desktop-ui/src/api/client.ts` lines 61, 65  
**Severity:** P2 — Information leak in production

```typescript
console.log('[API Client] Request to:', config.url, 'Token present:', !!token, ...);
console.log('[API Client] Added Authorization header');
```

These are debug logs that leak auth information to the browser console. Must be removed or gated behind `import.meta.env.DEV`.

---

## 🟡 INCONSISTENCIES

### INC-1: `actor_user_id` Type Inconsistency (int vs string)
Multiple API endpoints call `get_jwt_identity()` which returns a **string** (since `create_tokens` uses `identity=str(user.id)`). Some endpoints convert it (`int(get_jwt_identity())`), but others pass the string directly:

| File | Line | Converts? |
|------|------|-----------|
| `api/approvals.py` | 49 | ✅ `int()` |
| `api/draft_groups.py` | 57, 100, 133, 171 | ✅ `int()` |
| `api/inventory.py` (adjust) | 103 | ❌ String passed to service |
| `api/inventory.py` (count) | 282 | ❌ String passed to service |
| `api/inventory.py` (receive) | 330 | ❌ String passed to service |

The services use `db.session.get(User, actor_user_id)` which **may work** if SQLAlchemy auto-coerces, but it's fragile and inconsistent. All inventory endpoints should `int()` convert.

---

### INC-2: Missing `location_id` in `CreateDraftGroupPayload` (Frontend)
**File:** `desktop-ui/src/api/types.ts` line 213  
The `CreateDraftGroupPayload` type has no `location_id`, but the backend schema `DraftGroupCreateSchema` requires it. The `BulkDraftEntry.tsx` doesn't send `location_id` at all. This likely results in a 400 validation error unless Marshmallow has a default.

---

### INC-3: Inconsistent Error Handling Patterns
Some endpoints use `try/except` with manual error responses (`api/inventory.py`), while others let the global `AppError` handler in `error_handling.py` handle everything (`api/approvals.py`). The global handler is **safer** and more consistent. Manual `try/except` blocks should be removed where possible.

---

### INC-4: `StockReceiveRequestSchema` Imported Twice
**File:** `backend/app/api/inventory.py` line 21  
```python
from ..schemas.inventory import (
    ...
    StockReceiveRequestSchema,
    StockReceiveRequestSchema,  # ← duplicate import
    ...
)
```

---

## 🟢 IMPROVEMENTS

### IMP-1: Add Pagination to List Endpoints
`DraftGroup.query.order_by(...).all()` and `Transaction` queries load **all rows** into memory. For growing datasets, this will degrade performance. Add `page` / `per_page` query params with default limit (50).

### IMP-2: Add `is_paint` to Inventory Summary Response
The frontend `InventoryItem` type includes `is_paint` but the backend `InventorySummary` endpoint doesn't return it. The Inventory page could benefit from categorization (paint vs consumables).

### IMP-3: Replace Legacy `require_token` Decorator
`backend/app/auth.py` contains a legacy `require_token` decorator (line 138). If it's no longer used anywhere, delete it.

### IMP-4: Test Coverage Gaps
- No tests for `receiving_service` consumable path (system batch creation)
- `test_shortage_draft.py` is broken (BUG-2)
- No tests for `inventory_count` edge cases (counted = 0)
- No tests for `draft_group_service.create_group` consumable logic
- `test_auth_rate_limit.py` is very minimal (single test)

### IMP-5: Frontend — `Inventory.tsx` Missing Operator Access
Per `RULES_OF_ENGAGEMENT.md` Rule 12: Operators can "View inventory". But `App.tsx` wraps `/inventory` with `RequireAdmin`. Consider exposing a read-only inventory view to operators.

### IMP-6: Frontend — Receipt History Missing `user_name` Display
The backend sends `user_name` in receipt lines, but `ReceiptHistory.tsx` doesn't display it in the table. Add a "Received By" column.

### IMP-7: Frontend — Global Error Boundary
No React error boundary exists. If a component crashes, the entire app goes white. Add an `ErrorBoundary` wrapper.

### IMP-8: Backend — Missing `client_event_id` in `StockReceiveRequestSchema`
The schema doesn't include `client_event_id`, but the `receive_stock` service accepts it. Frontend can't send idempotency keys for receiving.

---

## 📊 Summary

| Category | Count | Priority |
|----------|-------|----------|
| 🔴 Bugs | 5 | P0: 2, P1: 2, P2: 1 |
| 🟡 Inconsistencies | 4 | Medium |
| 🟢 Improvements | 8 | Low-Medium |

---

## Next Steps

1. ✅ Create **TASK-0016-backend-bugfixes.md** → Backend Agent
2. ✅ Create **TASK-0017-frontend-cleanup.md** → Frontend Agent
