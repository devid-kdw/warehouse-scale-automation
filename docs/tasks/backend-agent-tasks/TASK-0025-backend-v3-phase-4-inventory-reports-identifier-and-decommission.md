# Task Brief: TASK-0025 — Backend v3 Phase 4 (Inventory, Reports, Identifier, Decommission)

**Created**: 2026-02-17  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Complete backend support for final v3 modules (`Skladište`, `Izvještaji`, `Article Identifikator`) and safely decommission obsolete contracts.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/backend-agent-tasks/TASK-0022-backend-v3-phase-1-foundation-and-migrations.md`
3. `docs/tasks/backend-agent-tasks/TASK-0023-backend-v3-phase-2-orders-and-receiving.md`
4. `docs/tasks/backend-agent-tasks/TASK-0024-backend-v3-phase-3-outbound-and-approvals.md`
5. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-005`, `S-007`, `S-008`, `S-009`, `S-011`)
6. `docs/team/RULES_OF_ENGAGEMENT.md` (RBAC + inventory discrepancy + reports restrictions)

---

## Scope

### In Scope

- Inventory backend for consolidated `Skladište`:
  - article list by article+batch,
  - category filters,
  - active/inactive/all,
  - inspect payload (batch quantities + last activity data),
  - admin create/edit/inactivate/reactivate support.
- Reports backend refactor:
  - inventory count list,
  - surplus list,
  - statistics baseline endpoints,
  - export endpoints (Excel/PDF) for required lists.
- Article Identifikator backend:
  - alias lookup,
  - missing-article report submission,
  - deduplicated queue,
  - admin resolve/close workflow.
- Decommission obsolete endpoints:
  - standalone `/api/batches` create endpoint,
  - old transaction-report-only shape once replacement is live.

### Out of Scope

- Frontend implementation.
- Hardware integration drivers.

---

## Technical Changes

### 1) Inventory Consolidation APIs

- Add/extend endpoints to support:
  - ordered list by article number,
  - category filtering,
  - active/inactive/all state filtering,
  - edit-safe descriptive fields (name, supplier/manufacturer, category, UOM, has_batch),
  - inspect detail payload including:
    - quantities by batch,
    - last received,
    - last issued,
    - last activity.

### 2) Reports Refactor APIs

- Replace raw transaction-table focus with module-level APIs:
  - `Inventurna lista` (article+batch rows; current vs counted state),
  - `Surplus lista`,
  - `Statistike` baseline endpoints:
    - article consumption view,
    - top 20 monthly consumers,
    - reorder-risk list with zones (green/yellow/red) where yellow = within 10% above threshold.
- Export support for Excel and PDF.

### 3) Article Identifikator APIs

- Lookup by alias/name/code normalization.
- Missing article report submission endpoint (ADMIN + OPERATOR allowed).
- Queue processing (ADMIN-only):
  - deduplicate equivalent reports,
  - mark resolved,
  - close explicitly.

### 4) Decommission and Compatibility Cleanup

- Remove or hard-deprecate outdated endpoints once replacements are stable.
- Ensure OpenAPI docs and error codes are aligned.

---

## Acceptance Criteria

1. [ ] Inventory APIs support required filters, inspect payload, and admin descriptive edits.
2. [ ] Reports APIs expose inventura/surplus/statistics endpoints with exports.
3. [ ] Identifier APIs support lookup + missing-report lifecycle with dedup and explicit close.
4. [ ] RBAC is correct: reports/admin processing are ADMIN-only, lookup/report submit available to OPERATOR.
5. [ ] Obsolete API paths are removed/deprecated per plan without hidden breakages.
6. [ ] Docs (`CHANGELOG`, `MIGRATIONS`, OpenAPI) are synchronized.

---

## Test Plan

### Automated

```bash
cd backend
pytest -v
```

### Focused

```bash
pytest tests/test_inventory.py -v
pytest tests/test_reports.py -v
pytest tests/test_aliases.py -v
pytest tests/test_rbac.py -v
```

### Manual Contract Checks

1. Inventory list ordering/filtering and inspect payload correctness.
2. Inventory count discrepancy behavior (shortage draft / surplus add) preserved.
3. Reports exports download correctly (Excel/PDF).
4. Missing-article report dedup + resolve + close flow.

---

## Rollout / Migration Notes

- Decommission is last step in v3 wave.
- Keep temporary compatibility endpoints until frontend Task-0029 is merged.
- Verify no consumers still call deprecated batch-create API before hard removal.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`
- [ ] `docs/team/MIGRATIONS.md`
- [ ] `docs/team/DECISIONS.md` (only if any policy detail changes)

---

## Status Updates

- 2026-02-17: Task created.

