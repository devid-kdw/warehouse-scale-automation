# Task Brief: TASK-0026B - Backend Runtime & Contract Stabilization

**Created**: 2026-02-17  
**Assigned to**: Backend Agent (new handover)  
**Status**: Ready for Implementation  
**Priority**: P0 (Release blocker)

---

## Goal

Stabilize backend runtime after v3 + remediation wave by removing broken `quantity_kg` references, fixing API/service contract mismatches, and delivering a clean unit-aware contract (`quantity` + `uom`) across active endpoints.

This task is strictly a **stabilization + correctness** pass. No new product features are introduced.

---

## Why This Task Exists

Current backend contains critical runtime issues identified in orchestrator recheck:

- `POST /api/inventory/receive` call mismatch (API passes `quantity_kg`, service no longer accepts it).
- Multiple API/service paths still reference removed DB/model fields (`quantity_kg`).
- Draft group update route calls a non-existing service method.
- Approvals response keys do not match service output keys.
- Draft/draft-group contracts are still KG-named while model is unit-aware.
- Inventory count service still writes/reads removed fields.

Reference:
- `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`

---

## Mandatory Reading Before Coding

1. `README.md`
2. `docs/team/RULES_OF_ENGAGEMENT.md`
3. `docs/team/DECISIONS.md`
4. `docs/team/AGENTS.md`
5. `docs/team/AGENT_INSTRUCTIONS.md`
6. `docs/team/WORKFLOW.md`
7. `docs/team/MIGRATIONS.md`
8. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
9. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
10. `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
11. `docs/tasks/backend-agent-tasks/TASK-0026A-backend-quantity-kg-decommission-and-remediation.md`
12. `docs/team/CHANGELOG.md`

If any conflict appears: follow authority order from `TASK-0021`.

---

## Hard Rules for This Task

1. Do **not** reintroduce `quantity_kg` columns in models or migrations.
2. Keep stock-changing runtime logic unit-aware (`quantity`, `uom`).
3. Preserve RBAC exactly per locked rules.
4. Preserve audit trail for all stock-changing operations.
5. Keep UTC storage and existing Europe/Berlin operational-day behavior for approvals.
6. Keep canonical admin Identifikator route family (`/api/admin/identifikator/*`).
7. Do not silently coerce unsupported unit conversions in stock-changing paths.

---

## Scope

### In Scope

- Runtime crash fixes and API/service mismatch fixes.
- Contract normalization for active (non-deprecated) endpoints.
- Model/schema/service cleanup for removed legacy fields.
- Test updates/additions for all touched flows.
- Docs/changelog synchronization.

### Out of Scope

- New feature development outside stabilization scope.
- Frontend implementation.
- Hardware integration features.

---

## Detailed Work Packages

## WP-0: Baseline & Safety

1. Create a short "baseline notes" section in PR/summary:
   - current migration head,
   - DB reset context (test data removed; keep bootstrap admin account),
   - active blocker list from audit doc.
2. Run static sanity check before edits:
   - `python3 -m compileall app`

---

## WP-1: Inventory Receive + Receipt History (Critical)

### Problems
- API passes unsupported argument into `receive_stock`.
- Receipt history aggregates using removed `tx.quantity_kg`.

### Required Changes
1. Fix `POST /api/inventory/receive` call signature alignment:
   - API must send only params accepted by `receive_stock`.
   - Remove `quantity_kg` argument from call path.
2. Ensure receive schema/API/service are consistent:
   - canonical input: `quantity`, `uom`,
   - conditional batch behavior by `article.has_batch`,
   - enforce required `delivery_note_number`,
   - ad-hoc requires `note` when `order_line_id` missing.
3. Fix receipt history aggregation:
   - use `tx.quantity`,
   - include `uom` in line and group payload,
   - no direct `quantity_kg` read from model.

### Primary Files
- `backend/app/api/inventory.py`
- `backend/app/schemas/inventory.py`
- `backend/app/services/receiving_service.py`

### Tests
- update/add tests in:
  - `backend/tests/test_receiving.py`
  - `backend/tests/test_inventory_receipts.py`

---

## WP-2: Drafts & Draft Groups Contract Alignment (Critical)

### Problems
- Draft schemas and APIs still KG-named.
- Draft group patch route calls non-existing service method.
- Draft group total property reads removed field.

### Required Changes
1. Convert Draft API contract to unit-aware:
   - request/response fields: `quantity`, `uom` (primary),
   - remove runtime dependence on `quantity_kg`.
2. Convert Draft Group line contract to unit-aware:
   - line input supports `quantity`, `uom`,
   - keep temporary compatibility alias only if safely mapped from/to `quantity` (no model `quantity_kg` access).
3. Fix draft-group update endpoint/service wiring:
   - route must call existing update service method (or rename consistently),
   - support `description` update path as required by v3.
4. Fix draft group totals:
   - compute from draft `quantity`,
   - expose unit-aware naming in active contract.

### Primary Files
- `backend/app/api/drafts.py`
- `backend/app/schemas/drafts.py`
- `backend/app/api/draft_groups.py`
- `backend/app/schemas/draft_groups.py`
- `backend/app/services/draft_group_service.py`
- `backend/app/models/draft_group.py`

### Tests
- update/add:
  - `backend/tests/test_draft_groups.py`
  - `backend/tests/test_daily_approvals.py`
  - `backend/tests/test_consumables_draft.py`

---

## WP-3: Inventory Count Service Unit-Aware Rewrite (Critical)

### Problems
- Service still creates/reads `quantity_kg` on models where field is removed.

### Required Changes
1. Rewrite count logic to use `Stock.quantity` and `Surplus.quantity`.
2. Ensure all created transactions use `quantity` + `uom`.
3. Ensure created shortage drafts use `quantity` + `uom`.
4. Keep business behavior unchanged:
   - OVER => add to surplus
   - EQUAL => no change
   - UNDER => reset surplus + create shortage draft

### Primary Files
- `backend/app/services/inventory_count_service.py`
- `backend/app/api/inventory.py` (count endpoint integration if needed)

### Tests
- update/add:
  - `backend/tests/test_inventory_count.py`

---

## WP-4: Approvals API/Schema Consistency (Critical)

### Problems
- Approvals API response keys mismatch service return keys.
- Schema still KG-named in response.

### Required Changes
1. Align `approve` response payload with actual service keys (or harmonize both layers).
2. Ensure schema reflects actual payload names.
3. Keep daily approvals route shape unchanged (`/<date>/<location_id>`).
4. Keep aggregation unit-aware and mixed-UOM validation behavior.

### Primary Files
- `backend/app/api/approvals.py`
- `backend/app/schemas/approvals.py`
- `backend/app/services/approval_service.py`

### Tests
- update/add:
  - `backend/tests/test_approval_service.py`
  - `backend/tests/test_daily_approvals.py`

---

## WP-5: Transactions Endpoint Cleanup (High)

### Problems
- `/api/transactions` still reads removed `tx.quantity_kg`.

### Required Changes
1. Replace transaction serialization to use:
   - `quantity`
   - `uom`
2. Keep response backward-compatible only if mapped safely from `quantity` (no direct removed-field access).
3. Ensure filters continue to work.

### Primary Files
- `backend/app/api/transactions.py`
- `backend/app/schemas/transactions.py`

### Tests
- add/update transaction endpoint tests accordingly.

---

## WP-6: Model Integrity Cleanup (High)

### Problems
- Duplicate `batch_id` declarations exist in at least two models.

### Required Changes
1. Remove duplicate column declarations:
   - `Surplus`
   - `WeighInDraft`
2. Ensure model metadata remains migration-compatible.
3. Run compile/import sanity checks after cleanup.

### Primary Files
- `backend/app/models/surplus.py`
- `backend/app/models/weigh_in_draft.py`

---

## WP-7: Inventory Summary & Consolidated Contracts (High)

### Problems
- Legacy summary path still uses removed fields.

### Required Changes
1. Ensure `/api/inventory` (consolidated) is authoritative and stable.
2. Fix `/api/inventory/summary` legacy implementation to avoid removed-field access, or explicitly deprecate/retire if no longer needed by locked scope.
3. Do not leave dead KG field references in active code paths.

### Primary Files
- `backend/app/api/inventory.py`
- `backend/app/schemas/inventory.py`
- `backend/app/services/inventory_service.py`

---

## WP-8: Quality Pass + Documentation

### Required Changes
1. Remove stale KG wording from error/details where misleading.
2. Update docs:
   - `docs/team/CHANGELOG.md`
   - `docs/team/MIGRATIONS.md` (if migration behavior clarified)
   - `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md` (append completion note, do not overwrite findings)
3. Keep deprecated/fallback routes clearly labeled.

---

## API Contract Target (Post-Task)

For active non-deprecated stock/draft flows:

- Quantity payload fields must be `quantity` + `uom`.
- Any temporary `*_kg` alias in response must be derived from `quantity` and must not be required by clients.
- No endpoint may read non-existent model attributes.

---

## Acceptance Criteria

1. [ ] No active runtime path reads removed model fields (`quantity_kg`).
2. [ ] `POST /api/inventory/receive` works with aligned API-service signature.
3. [ ] Draft and draft-group flows are unit-aware and runtime-stable.
4. [ ] Inventory count flow runs without legacy-field access and keeps business behavior.
5. [ ] Approvals endpoint responses match schemas and service payloads.
6. [ ] `/api/transactions` response no longer dereferences removed fields.
7. [ ] Duplicate model field declarations removed.
8. [ ] Static compile passes.
9. [ ] Test suite passes in project environment.
10. [ ] Docs/changelog updated.

---

## Test Plan

## Automated (minimum)

```bash
cd backend
pytest -v
```

## Focused suites

```bash
pytest tests/test_receiving.py -v
pytest tests/test_inventory_receipts.py -v
pytest tests/test_inventory_count.py -v
pytest tests/test_draft_groups.py -v
pytest tests/test_daily_approvals.py -v
pytest tests/test_approval_service.py -v
pytest tests/test_inventory_service.py -v
pytest tests/test_orders.py -v
```

## Additional sanity

```bash
python3 -m compileall app
python3 -c "from app import create_app; app=create_app(); print('app-init-ok')"
```

---

## Delivery Format Required from Agent

After completion, agent must return:

1. Summary of implemented fixes by work package (`WP-1` ... `WP-8`).
2. Full list of changed files.
3. Exact tests run + pass/fail results.
4. Any remaining risks/blockers.
5. Explicit frontend-impact note:
   - endpoints now safe for frontend integration,
   - endpoints still blocked (if any).

---

## Status Updates

- 2026-02-17: Task created from orchestrator recheck after backend v3 remediation loop.
