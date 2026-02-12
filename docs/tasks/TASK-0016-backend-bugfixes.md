# Task Brief: TASK-0016 — Backend Bug Fixes & Hardening

**Created**: 2026-02-10  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0-Critical (BUG-1, BUG-4), P1-High (BUG-2, BUG-3), P2-Medium (INC-1, INC-4)  
**Source**: [Orchestrator Review](../status/ORCHESTRATOR_REVIEW_2026-02-10.md)

---

## 🎯 Goal

Fix critical bugs in backend services and API layer identified during orchestrator code review.

---

## 📋 Scope

### In Scope
- [BUG-1] Remove duplicate `batch_id` resolution in `draft_group_service.create_group()`
- [BUG-2] Fix `test_shortage_draft.py` to test actual approval logic
- [BUG-3] Fix AttributeError in `api/inventory.py` count endpoint error handler
- [BUG-4] **Change all `location_id` defaults from `1` to `13`**
- [INC-1] Normalize `actor_user_id` type across all inventory API endpoints
- [INC-4] Remove duplicate `StockReceiveRequestSchema` import
- [IMP-3] Remove legacy `require_token` decorator if unused
- [IMP-8] Add `client_event_id` to `StockReceiveRequestSchema`

### Out of Scope
- Pagination (IMP-1) — separate task
- New test coverage (IMP-4) — separate task

---

## 🔧 Technical Changes

### 1. `backend/app/services/draft_group_service.py`

**Problem:** Lines 100–112 duplicate the batch_id resolution logic from lines 72–81.

**Fix:** Delete lines 100–112 entirely. The first block (72–81) already handles:
- `batch_id is None` + `is_paint` → `AppError('BATCH_REQUIRED')`
- `batch_id is None` + consumable → `get_or_create_system_batch()`

After deletion, the loop body should flow directly from quantity rounding (line 94) to the `WeighInDraft(...)` creation (line 114).

---

### 2. `backend/tests/test_shortage_draft.py`

**Problem:** Tests post to `/api/approvals/{id}/approve` (404), but the real endpoint is `/api/drafts/{id}/approve`.

**Fix:**
```diff
 # Line 41
-response = client.post(f'/api/approvals/{shortage_draft}/approve', headers=headers)
-assert response.status_code == 200
+response = client.post(f'/api/drafts/{shortage_draft}/approve', headers=headers)
+assert response.status_code == 200

 # Line 66
-response = client.post(f'/api/approvals/{shortage_draft}/approve', headers=headers)
-assert response.status_code == 409
+response = client.post(f'/api/drafts/{shortage_draft}/approve', headers=headers)
+assert response.status_code == 409
```

Verify tests pass with `pytest backend/tests/test_shortage_draft.py -v`.

---

### 3. `backend/app/api/inventory.py` — InventoryCount error handler

**Problem:** Lines 296–304 reference `e.error_code` and `e.status_code` which don't exist on `AppError`.

**Fix (Option A — Preferred):** Remove the `try/except` entirely and let the global `AppError` handler manage it. This is consistent with the approval endpoints.

**Fix (Option B — Quick):**
```diff
 except AppError as e:
     db.session.rollback()
-    return {
-        'error': {
-            'code': e.error_code,
-            'message': e.message,
-            'details': e.details
-        }
-    }, e.status_code
+    raise  # Let global handler deal with it
```

---

### 4. Location ID: Change ALL Defaults from `1` to `13` (P0-CRITICAL)

> [!CAUTION]
> Per RULES_OF_ENGAGEMENT.md Rule 3 and Stefan's explicit confirmation: **Location ID is 13.** The field must remain configurable, but the default must be `13`.

**Files to change:**

#### `backend/app/services/receiving_service.py`
```diff
 def receive_stock(
     ...
-    location_id: int = 1,
+    location_id: int = 13,
     ...
 ):
-    """... (default=1, only 1 allowed in v1)"""
+    """... (default=13, primary warehouse location)"""

 # v1: Only location_id=13 allowed
-    if location_id != 1:
+    if location_id != 13:
         raise AppError(
             'LOCATION_NOT_ALLOWED',
-            'Only location_id=1 is allowed in v1',
+            'Only location_id=13 is allowed in v1',
```

#### `backend/app/api/inventory.py`
```diff
 # Line 207 (InventorySummary default)
-target_location_id = location_id if location_id else 1
+target_location_id = location_id if location_id else 13

 # Line 340 (InventoryReceive default)
-location_id=data.get('location_id', 1),
+location_id=data.get('location_id', 13),
```

#### `backend/app/schemas/inventory.py`
```diff
 # InventoryCountRequestSchema (line 42)
-location_id = fields.Integer(load_default=1, ...)
+location_id = fields.Integer(load_default=13, ...)

 # StockReceiveRequestSchema (line 90)
-location_id = fields.Integer(load_default=1, ...)
+location_id = fields.Integer(load_default=13, ...)
```

> [!IMPORTANT]
> Also verify that the Location record with `id=13` exists in the database seed. Check `backend/app/cli.py` or seed files.

---

### 5. `backend/app/api/inventory.py` — `actor_user_id` type

**Fix:** Add `int()` conversion in all three inventory endpoints:
```python
# InventoryAdjust.post (line 103)
actor_user_id = int(get_jwt_identity())

# InventoryCount.post (line 282)
actor_user_id = int(get_jwt_identity())

# InventoryReceive.post (line 330)
actor_user_id = int(get_jwt_identity())
```

---

### 6. `backend/app/api/inventory.py` — Duplicate import

**Fix:** Remove the duplicate `StockReceiveRequestSchema` on line 21.

---

### 7. `backend/app/auth.py` — Legacy decorator

**Action:** Search codebase for `require_token` usage. If no files import it, delete lines 137–148.

---

### 8. `backend/app/schemas/inventory.py` — Add `client_event_id`

**Fix:** Add to `StockReceiveRequestSchema`:
```python
client_event_id = fields.String(
    allow_none=True,
    validate=validate.Length(max=100),
    metadata={'description': 'Optional client-generated UUID for idempotency'}
)
```

---

## ✅ Acceptance Criteria

1. [ ] `create_group()` has no duplicate batch_id logic
2. [ ] `test_shortage_draft.py` posts to correct endpoint and passes
3. [ ] Inventory count endpoint handles errors without AttributeError
4. [ ] **All `location_id` defaults are `13`** (not `1`)
5. [ ] All `get_jwt_identity()` calls in inventory routes convert to `int`
6. [ ] No duplicate imports
7. [ ] Legacy `require_token` removed if unused
8. [ ] `client_event_id` accepted in stock receive schema
9. [ ] All existing tests pass: `pytest backend/tests/ -v`

---

## 🧪 Test Plan

```bash
# Run all tests
pytest backend/tests/ -v

# Specifically verify shortage draft fix
pytest backend/tests/test_shortage_draft.py -v

# Verify draft group creation still works
pytest backend/tests/test_draft_groups.py -v

# Verify inventory endpoints
pytest backend/tests/test_inventory_service.py -v
pytest backend/tests/test_inventory_count.py -v
```

---

## 📚 Related Documentation

- [Orchestrator Review](../status/ORCHESTRATOR_REVIEW_2026-02-10.md)
- [RULES_OF_ENGAGEMENT.md](../team/RULES_OF_ENGAGEMENT.md) — Locked rules (Location ID = 13)
- [CHANGELOG.md](../team/CHANGELOG.md) — Must update after fixes

---

**Status Updates**:
- 2026-02-10: Task created from Orchestrator Review
