# Task Brief: TASK-0029 — Frontend v3 Phase 4 (Skladište, Izvještaji, Article Identifikator)

**Created**: 2026-02-17  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Deliver final v3 UI modules and decommission legacy screens by consolidating inventory/article workflows and introducing new reports/identifier experiences.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/frontend-agent-tasks/TASK-0026-frontend-v3-phase-1-shell-i18n-layout.md`
3. `docs/tasks/backend-agent-tasks/TASK-0025-backend-v3-phase-4-inventory-reports-identifier-and-decommission.md`
4. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-005`, `S-007`, `S-009`, `S-011`)
5. `docs/team/RULES_OF_ENGAGEMENT.md`
6. `docs/team/DECISIONS.md`
7. `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
8. `docs/tasks/backend-agent-tasks/TASK-0026B-backend-runtime-contract-stabilization.md`

---

## Backend Gate (Current)

Per latest backend audit:
- Use consolidated inventory contract (`GET /api/inventory`) and inspect contract.
- Use canonical admin identifikator routes only.
- Legacy/fallback routes remain out of scope for new UI.

---

## Scope

### In Scope

- Inventory screen -> `Skladište` with title `Pregled artikala`.
- Replace paint/consumables tabs with category filtering.
- Add table columns and behaviors per approved structure:
  - article number,
  - article description,
  - supplier,
  - batch,
  - quantity,
  - last activity date,
  - actions (`Edit article`, `Inspect article`).
- Integrate article admin actions in inventory:
  - add article,
  - edit descriptive fields,
  - set inactive/reactivate,
  - active/inactive/all filters.
- Reports module -> `Izvještaji` with sub-screens:
  - `Inventurna lista`,
  - `Surplus lista`,
  - `Statistike`.
- Implement baseline statistics visuals and lists.
- Implement `Article Identifikator` module UI:
  - lookup flow for OPERATOR + ADMIN,
  - missing-article submit flow,
  - admin processing queue (hosted under reports as agreed).
- Remove legacy standalone `Articles` and old `Reports` transaction-table UI from navigation.

### Out of Scope

- Backend API implementation.
- Final KPI tuning beyond baseline charts/lists.

---

## Technical Changes

### 1) Skladište Consolidation

- Merge old inventory + articles UX into one module.
- Ensure category filter list uses approved category set and Croatian labels.
- Keep admin-only guard for add/edit/inactivate actions.
- Use current backend routes:
  - consolidated list: `GET /api/inventory`
  - inspect: `GET /api/inventory/<article_id>/inspect`
  - article create/list/archive/restore/update: existing `/api/articles*` endpoints
- Use canonical fields (`quantity`, `uom`, `stock`, `surplus`, `total`) and avoid introducing legacy KG mappings in new UI code.

### 2) Izvještaji Redesign

- Replace raw transaction table with report submodules.
- Support exports where backend provides downloadable endpoints.
- Render reorder-risk zones with color logic (green/yellow/red).
- Backend route alignment:
  - `GET /api/reports/inventurna` (+ `/export/excel`, `/export/pdf`)
  - `GET /api/reports/surplus` (+ `/export/excel`, `/export/pdf`)
  - `GET /api/reports/statistics/consumption`
  - `GET /api/reports/statistics/reorder-risk`
  - `GET /api/reports/statistics/top-consumers`
  - `GET /api/reports/statistics/reporting`
- Do not build new UI dependency on deprecated fallback endpoint `/api/reports/transactions`.

### 3) Article Identifikator UX

- Fast lookup input for alias/name/code.
- Missing-item report submit if no match.
- Admin queue view for processing deduplicated requests and close/resolve actions.
- Use canonical admin contract:
  - `GET /api/admin/identifikator/queue`
  - `PATCH /api/admin/identifikator/queue/<id>`
- Legacy admin Identifikator routes are fallback-only and should not be used by new UI flows.

### 4) Legacy Screen Decommission

- Remove `/articles` standalone route.
- Remove old reports transaction-list UI.
- Keep route redirects/fallbacks if required for safe transition.

---

## Acceptance Criteria

1. [ ] `Skladište` replaces old inventory/articles split and includes required filters/actions.
2. [ ] `Izvještaji` contains `Inventurna lista`, `Surplus lista`, and `Statistike` sub-screens.
3. [ ] `Article Identifikator` workflows are accessible to OPERATOR + ADMIN with role-correct actions.
4. [ ] Legacy `Articles` and old `Reports` screens are removed from active navigation.
5. [ ] Build passes and RBAC visibility remains correct.
6. [ ] Frontend integrates with canonical backend routes listed in this task (without relying on deprecated fallback APIs).

---

## Test Plan

### Automated

```bash
cd desktop-ui
npm run build
```

### Manual

1. Verify category filtering and table sorting in `Skladište`.
2. Verify add/edit/inactivate actions as ADMIN and read-only behavior for OPERATOR.
3. Verify reports sub-screens and exports.
4. Verify Article Identifikator lookup + missing report submit + admin processing view.
5. Verify removed legacy routes are not visible in sidebar.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`

---

## Status Updates

- 2026-02-17: Task created.
