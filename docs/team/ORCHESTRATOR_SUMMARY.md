# Orchestrator Summary - Stabilization Phase

**Status**: P0 - STOP FEATURE DEV. FIX BLOCKERS.

**Goal**: "App starts, migrations work, Draft Groups work E2E, Bulk Entry is available."

---

## 🚨 P0 - Critical Blockers (Immediate)

### Backend Agent
- **Target**: `DraftGroup` Export & Migrations.
- **DoD**:
  - `python -c "from app.models import DraftGroup"` succeeds.
  - `flask db upgrade` succeeds (Schema matches ORM).
  - `DraftGroup` table exists with correct FKs.
  - `WeighInDraft` has `draft_group_id`.
  - API Enpoints (`GET`, `POST`, `POST /{id}/approve`) wired and working.
  - Atomicity check (409 rollback) verified.

### Frontend Agent
- **Target**: Expose Bulk Entry.
- **DoD**:
  - Route `/drafts/bulk` added.
  - Sidebar link "Bulk Entry" (Admin-only guard).
  - Legacy cleanup (`useAppSettings`, `STORAGE_KEYS`).
  - Build without warnings.

---

## 🔒 P1 - Security & Tests (Next)

### Backend Agent
- **Rate Limiting**: `Flask-Limiter` on `/api/auth/login` (6/min).
- **Tests**: 4 core tests for Draft Groups (Create, Approve, Insufficient Stock -> 409, Reject).

---

## 📝 P2 - Nice to Have (Later)
- Docs update (CHANGELOG).
- FE Unit Tests.
- dedicated Draft Group management page (if needed).
