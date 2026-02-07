# TASK-0012: Backend Stabilization (P0/P1)

**Goal**: Ensure database models are exported, migrations are synced, and critical API functionality (Draft Groups) works end-to-end with Atomicity.

**Assigned to**: Backend Agent

---

## 🚨 P0 - Critical Blockers

### 1. DraftGroup Export & Relationships
- [ ] **File**: `backend/app/models/__init__.py`: Ensure `DraftGroup` is exported.
- [ ] **File**: `backend/app/models/weigh_in_draft.py`:
  - Verify `draft_group_id` column.
  - Verify `draft_group` relationship (Backref correct?).
- [ ] **File**: `backend/app/models/draft_group.py`:
  - Verify `drafts` relationship aligns with `WeighInDraft`.

### 2. Migrations & Database (Sync check)
- [ ] **Run Check**: `python -c "from app.models import DraftGroup"`. Must succeed.
- [ ] **Run Check**: `flask db upgrade`.
  - Ensure `draft_groups` table exists.
  - Ensure `weigh_in_drafts` has `draft_group_id` FK.
  - **Status Fix**: If `add_draft_groups_manual.py` causes issues, convert content to valid revision file or fix manual state.

### 3. API Wiring
- [ ] **Verify**: `draft_groups` blueprint registered in `create_app`.
- [ ] **Verify Endpoints**:
  - `GET /api/draft-groups` (Admin) -> 200 OK.
  - `POST /api/draft-groups` (Bulk Create) -> 201 Created.
  - `POST /api/draft-groups/{id}/approve` -> 200 OK (with atomic logic).
- [ ] **Legacy Compat**: Verify single draft creation still works.

---

## 🔒 P1 - Security & Tests

### 4. Rate Limiting
- [ ] **Install**: `Flask-Limiter` (if not present).
- [ ] **App**: Initialize Limiter.
- [ ] **Route**: Apply limit `6 per minute` to `/api/auth/login`.
- [ ] **Verify**: 7th attempt returns 429.

### 5. Automated Tests (Draft Groups)
- [ ] **Create**: `tests/test_draft_groups.py` -> Test bulk creation (2 lines).
- [ ] **Approve Success**: Test surplus-first consumption logic.
- [ ] **Approve Fail (Atomicity)**:
  - Create group with 1 valid line + 1 invalid line (insufficient stock).
  - Call Approve.
  - Assert: Response 409. Group status remains `DRAFT`. **NO STOCK CHANGED**.
- [ ] **Reject**: Test group rejection.

---

## ✅ Verification Steps (Backend)

1.  **Import**: `from app.models import DraftGroup` works.
2.  **Migration**: `flask db upgrade` is clean.
3.  **Tests**: `pytest tests/test_draft_groups.py` passes all 4 scenarios.
