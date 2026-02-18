# Task Brief: TASK-0026A - Backend `quantity_kg` Decommission & Remediation

**Created**: 2026-02-17  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Completely remove legacy `quantity_kg` as a canonical backend model across stock flows, and harden all related APIs/services/tests to a consistent unit-aware contract (`quantity` + `uom`).

---

## Mandatory Reading Before Coding

1. `docs/team/RULES_OF_ENGAGEMENT.md` (Rules 1, 2, 3, 6, 8, 9, 14, 17, 18)
2. `docs/team/DECISIONS.md` (2026-02-17 multi-unit + has_batch decisions)
3. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
4. `docs/tasks/backend-agent-tasks/TASK-0022-backend-v3-phase-1-foundation-and-migrations.md`
5. `docs/tasks/backend-agent-tasks/TASK-0023-backend-v3-phase-2-orders-and-receiving.md`
6. `docs/tasks/backend-agent-tasks/TASK-0024-backend-v3-phase-3-outbound-and-approvals.md`
7. `docs/tasks/backend-agent-tasks/TASK-0025-backend-v3-phase-4-inventory-reports-identifier-and-decommission.md`
8. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`

---

## Current Backend Audit Feedback (Must Be Addressed)

### Critical

1. `approval_service.py` silently sets `quantity_kg = 0` for unsupported UOM in aggregate edit fallback, which can corrupt pending draft mass values.  
   Reference: `backend/app/services/approval_service.py:515-517`
2. Daily and approval transaction paths still hardcode `uom='KG'` in multiple places, conflicting with unit-aware contract.  
   Reference: `backend/app/services/approval_service.py:163`, `backend/app/services/approval_service.py:182`, `backend/app/services/approval_service.py:265`
3. `receive_stock` accepts arbitrary request UOM and does not enforce article UOM authority before write.  
   Reference: `backend/app/services/receiving_service.py:73-95`

### High

1. Reports still aggregate/sort by `quantity_kg`; consumption rankings are mathematically wrong because consumed values are negative and sorted descending.  
   Reference: `backend/app/services/report_service.py:83-90`, `backend/app/services/report_service.py:166-173`
2. Draft group update contract is still legacy name-only (`description` not wired for PATCH flow).  
   Reference: `backend/app/schemas/draft_groups.py:62-64`, `backend/app/api/draft_groups.py:99-108`, `backend/app/services/draft_group_service.py:127-143`
3. Inventory/report schemas and APIs still expose KG-centric fields (`*_kg`) as primary response contract despite v3 unit-aware direction.  
   Reference: `backend/app/schemas/inventory.py:227-235`, `backend/app/schemas/reports.py:12-15`, `backend/app/schemas/reports.py:91`

### Medium

1. Duplicate import and minor quality issues in report service (`db` imported twice).  
   Reference: `backend/app/services/report_service.py:7-8`
2. Legacy validation helpers still reference `quantity_kg` in error messages and API semantics.  
   Reference: `backend/app/services/validation.py:56`, `backend/app/services/validation.py:117`, `backend/app/services/validation.py:129`

---

## Scope

### In Scope

- Full backend decommission of `quantity_kg` from:
  - models,
  - services,
  - schemas,
  - APIs,
  - tests,
  - migrations/docs.
- Unit-aware contract hardening:
  - `quantity` + `uom` everywhere,
  - article UOM authority enforcement,
  - no KG-only fallback paths in runtime logic.
- Remediation items listed in this task's audit feedback section.

### Out of Scope

- Frontend implementation (separate FE wave).
- Hardware integration device drivers.

---

## Technical Plan

### Phase A - Canonical Unit Model Hardening

1. Make `quantity` + `uom` canonical for `stock`, `surplus`, `weigh_in_drafts`, `transactions`.
2. Enforce NOT NULL (where not already enforced) and service-level guarantees:
   - `uom` required and normalized uppercase.
   - Request `uom` must match `article.uom` for stock-changing operations.
3. Remove write-time dependence on `quantity_kg` in:
   - receiving,
   - approvals,
   - inventory adjustment,
   - inventory count.

### Phase B - Remove Legacy Columns and KG Contracts

1. DB migration:
   - drop `quantity_kg` from `transactions`, `stock`, `surplus`, `weigh_in_drafts`.
   - drop legacy check constraints tied only to `quantity_kg`.
   - recreate equivalent constraints on `quantity` (non-negative/positive by table semantics).
2. Update model classes and `to_dict()` outputs to remove `quantity_kg`.
3. Remove `quantity_kg` from all schemas, request payloads, and response payloads.
4. Remove legacy compatibility branches (e.g. `quantity_kg` request fallback in receiving API).

### Phase C - Service and Report Refactor

1. Refactor report calculations to use unit-aware quantities.
2. Correct consumption ranking logic (absolute consumed quantity and correct order direction).
3. Standardize approvals daily aggregates:
   - strict single-UOM per aggregate group,
   - reject mixed-UOM groups with explicit error,
   - remove KG fallback/hardcoding.
4. Fix draft-group description update path end-to-end (create + patch + service).

### Phase D - Cleanup and Documentation

1. Remove KG-only wording from validation/errors/API docs.
2. Update:
   - `docs/team/CHANGELOG.md`
   - `docs/team/MIGRATIONS.md`
   - `docs/team/DECISIONS.md` (if any policy clarification required)
3. Add migration notes with rollback path and data integrity checks.

---

## Required API Contract Changes

1. `POST /api/inventory/receive`: remove `quantity_kg` request input.
2. `GET /api/inventory`, `GET /api/inventory/summary`, inspect payloads: remove `*_kg` primary fields.
3. Reports payloads: convert KG-centric fields to unit-aware (`quantity`, `uom`, explicit meaning).
4. Transactions payload: remove `quantity_kg` field from canonical response shape.

---

## Acceptance Criteria

1. [ ] No runtime service path writes or reads `quantity_kg`.
2. [ ] `quantity_kg` columns are removed from all relevant DB tables through migration.
3. [ ] All stock-changing APIs accept/use only `quantity` + `uom`.
4. [ ] Approval and receiving flows enforce article-UOM consistency.
5. [ ] Report math and ordering are correct for consumption and reorder views.
6. [ ] Draft-group `description` is fully writable/readable in create + patch.
7. [ ] Full test suite passes in project test environment.
8. [ ] Docs/changelog/migrations are synchronized.

---

## Test Plan

### Automated

```bash
cd backend
pytest -v
```

### Focused

```bash
pytest tests/test_receiving.py -v
pytest tests/test_daily_approvals.py -v
pytest tests/test_inventory_service.py -v
pytest tests/test_inventory_count.py -v
pytest tests/test_report_service.py -v
pytest tests/test_remediation_verification.py -v
```

### Migration Verification

```bash
flask db upgrade
flask db downgrade -1
flask db upgrade
```

Verify:
- data preserved,
- no null/invalid `quantity` + `uom`,
- no orphaned API references to `quantity_kg`.

---

## Rollout / Risk Notes

1. This is a breaking backend contract change. Frontend must switch to unit-aware payloads first or in same release window.
2. Perform migration in controlled window with DB backup.
3. If rollback needed, include reverse migration strategy that recreates `quantity_kg` safely (derived where possible).

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`
- [ ] `docs/team/MIGRATIONS.md`
- [ ] OpenAPI docs for all changed endpoints
- [ ] Any affected backend task docs in this folder

---

## Status Updates

- 2026-02-17: Task created from orchestrator backend audit after v3 remediation wave.
