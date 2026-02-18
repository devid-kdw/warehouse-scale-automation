# Task Brief: TASK-0028 — Frontend v3 Phase 3 (Izlaz & Approvals UI)

**Created**: 2026-02-17  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Refactor draft-entry, outbound (`Izlaz`), and approvals UX to match daily list operations and operator/admin realities.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/frontend-agent-tasks/TASK-0026-frontend-v3-phase-1-shell-i18n-layout.md`
3. `docs/tasks/backend-agent-tasks/TASK-0024-backend-v3-phase-3-outbound-and-approvals.md`
4. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-001`, `S-002`, `S-006`)
5. `docs/team/RULES_OF_ENGAGEMENT.md` (RBAC + timezone + approvals)
6. `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
7. `docs/tasks/backend-agent-tasks/TASK-0026B-backend-runtime-contract-stabilization.md`

---

## Backend Gate (Current)

Per latest backend audit and TASK-0026B, draft/draft-group/approvals contracts are stabilized.
Implement direct API integration using canonical `quantity` + `uom` contract.

---

## Scope

### In Scope

- Draft Entry screen (`Automatski unos`) refactor:
  - remove subtitle,
  - remove single/bulk tab switch,
  - default entry mode = scale (first load),
  - remove visible `Client Event ID`,
  - remove `My Recent Drafts` block,
  - hide location selector in v1.
- Bulk Entry screen refactor to `Izlaz`:
  - rename and relabel,
  - use system-assigned `Broj izlaza`,
  - add group-level description,
  - row model: article number + description + UOM + quantity (+ conditional batch),
  - remove unnecessary columns (`Mfr`, row-level note).
- Approvals redesign:
  - list by day,
  - row grouping by same article+batch,
  - list-level actions (approve/reject/edit),
  - time-only column inside same-day list,
  - admin-only screen.

### Out of Scope

- Orders screens (Phase 2).
- Inventory/reports/identifier screens (Phase 4).

---

## Technical Changes

### 1) Draft Entry UX Simplification

- Keep the screen focused on automatic scale-driven entry.
- Maintain backend idempotency behavior while hiding technical identifiers.

### 2) Izlaz Table UX

- Support article number-driven input and auto description hints.
- Quantity label must be `Količina` (unit-aware, no hardcoded KG).
- Batch field should render only for batch-tracked articles.
- Current backend contract mapping:
  - Draft group line create/read uses `quantity` + `uom`.
  - Frontend should not send legacy `quantity_kg` payload in new flows.

### 3) Approvals Day-Based Workflow

- Replace per-entry action grid with day-level processing flow.
- Support inline edit of pending quantities before final approval.
- Ensure status and actions are clearly scoped to list/day level.
- Route alignment (current backend):
  - `GET /api/drafts/daily`
  - `GET /api/drafts/daily/<date>/<location_id>`
  - `POST /api/drafts/daily/<date>/<location_id>/approve|reject`
  - `PATCH /api/drafts/daily/<date>/<location_id>/lines`
- For daily detail use `total_qty + uom` as primary display value.

---

## Acceptance Criteria

1. [ ] Draft Entry screen matches approved simplified UX.
2. [ ] `Izlaz` screen supports new group metadata and revised row structure.
3. [ ] Approvals are rendered and processed at day-list level.
4. [ ] Same article+batch repeats are shown as aggregated row; different batch remains separate.
5. [ ] OPERATOR cannot access admin-only approvals actions.
6. [ ] Build passes and no runtime route errors occur.
7. [ ] Frontend uses current approvals route shape with `location_id` path segment.
8. [ ] Outbound and approvals flows use canonical `quantity` + `uom` payload/response mapping.

---

## Test Plan

### Automated

```bash
cd desktop-ui
npm run build
```

### Manual

1. Open Draft Entry and verify removed elements + scale default behavior.
2. Create outbound draft in `Izlaz` with and without batch-tracked article.
3. Verify outbound create/update and day-approval flows against live backend routes.
4. Open Approvals as ADMIN, verify day grouping and list-level actions.
5. Login as OPERATOR and verify approvals actions are not accessible.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`

---

## Status Updates

- 2026-02-17: Task created.
