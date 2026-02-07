# TASK-0001: Draft Groups Implementation

## Goal
Implement a Grouping mechanism for drafts to support multiple line items (articles/batches) in a single header, allowing for atomic approval/rejection of a collection of inventory changes.

## Scope
### IN
- **Database**:
  - `draft_groups` table (id, name, status, source, location_id, created_at, created_by_user_id).
  - `weigh_in_drafts`: Add `draft_group_id` FK (RESTRICT on delete).
  - **Indices**:
    - `idx_weigh_in_drafts_group_id`
    - `idx_draft_groups_status_created_at`
    - `idx_draft_groups_source_created_at` (optional/recommended)
  - **Migration**: 
    - 2-step process: Add nullable `draft_group_id`, backfill existing drafts (batching 500/1000), then `ALTER to NOT NULL`.
- **API**:
  - `POST /api/draft-groups`: Create group with multiple lines.
  - `GET /api/draft-groups`: Summary list (includes `line_count`, `total_quantity_kg`, `created_by`, `source`).
  - `GET /api/draft-groups/:id`: Detail view with nested lines.
  - `PATCH /api/draft-groups/:id`: Rename group.
  - `POST /api/draft-groups/:id/approve`: Atomic approval.
  - `POST /api/draft-groups/:id/reject`: Atomic rejection.
- **Service Logic (Locked Rules)**:
  - **Status Sync**: Group state defines line state. Block double-actions (e.g. approving already approved) with 409 Conflict.
  - **Atomic Pre-check**: In `approve_group`, lock inventory rows `FOR UPDATE` (consistent order) and verify total availability before updating any single row or creating transaction logs.
  - **No Internal Commits**: Services must use passed session or only commit at the very end of the service call.
  - **Quantities**: Standardized `Decimal` with `ROUND_HALF_UP` and `0.01` quantization.
- **Idempotency**: Maintain `client_event_id` uniqueness on lines.

### OUT
- UI changes (handled by Frontend Agent).
- Multi-location support.

## Acceptance Criteria
- [ ] Existing `POST /api/drafts` creates an auto-named group (`AutoSingleDraft_YYYYMMDD_HHMMSS`) with source `ui_operator`.
- [ ] Group approval is all-or-nothing (atomic) with failure on insufficient stock for any line item.
- [ ] Database enforces `NOT NULL` on `draft_group_id` after migration.
- [ ] Idempotency via `client_event_id` is unique on line items.
- [ ] 409 Conflict returned when performing actions on already processed groups.

## Test Plan
- **Backend Tests** (`backend/tests/test_draft_groups.py`):
  - Test group creation (single vs multiple lines).
  - Test atomicity: 1 valid line + 1 insufficient stock line -> whole group fails.
  - Test double-approval/rejection (409).
  - Test migration backfill logic in batches.
  - Test precision summing (3 lines with small decimals).
