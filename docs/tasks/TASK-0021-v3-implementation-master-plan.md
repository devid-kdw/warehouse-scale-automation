# TASK-0021: v3.0 Implementation Master Plan

**Created**: 2026-02-17  
**Owner**: Orchestrator  
**Status**: Planning Ready  
**Version Target**: v3.0.0 (next program version)

---

## Goal

Implement the approved TASK-0020 redesign as a phased, low-risk delivery: unit-aware domain model, Orders module, Inventory consolidation, Reports refactor, Article Identifikator, and full Croatian-first UI with i18n.

---

## Planning Inputs (Authoritative)

1. `docs/team/RULES_OF_ENGAGEMENT.md`
2. `docs/team/DECISIONS.md`
3. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
4. `docs/team/WORKFLOW.md`

If any conflict appears during implementation, apply authority order above.

---

## Version Scope (v3.0.0)

### In Scope

- Unit-aware UX/API direction (no KG-only UI assumptions for new work).
- Batch behavior based on article flag `has_batch` (not `is_paint`).
- New `Narudžbe` module with sub-screens:
  - `Otvorene narudžbe`
  - `Ulaz robe`
  - `Zatvorene narudžbe`
- Receiving logic with `delivery_note_number` and optional `order_line_id`, plus ad-hoc receiving with note.
- Outbound flow (`Izlaz`) and Draft/Approvals redesign (daily grouping + list-level actions).
- Inventory consolidation (`Skladište`) including article-management actions (ADMIN-only) and inspect flow.
- Reports refactor to `Izvještaji` (`Inventurna lista`, `Surplus lista`, `Statistike`).
- New `Article Identifikator` module and missing-article report lifecycle.
- Croatian-first UI with language switcher (`hr`, `en`, `de`, `hu`) and shared layout tokens.
- Decommission of standalone `/articles`, `/batches`, and `/inventory/receipts` screens (after migration).

### Out of Scope

- Hardware device integration (scale/scanner drivers). Only canonical fields and contracts are prepared.
- Advanced statistics tuning/final KPI formulas beyond v1 baseline.
- Multi-location rollout (location remains fixed to ID 13 in v1).

---

## Delivery Strategy

Implementation is split into 4 backend tasks and 4 frontend tasks. Execution is phase-based: core foundation first, then dependent modules.

Post-backend-implementation note:
- Backend v3 wave is implemented, but recheck found critical runtime inconsistencies during `quantity_kg` decommission.
- Frontend phases must follow current backend contract snapshot:
  - `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
- Full legacy `quantity_kg` removal is tracked separately in:
  - `docs/tasks/backend-agent-tasks/TASK-0026A-backend-quantity-kg-decommission-and-remediation.md`

### Phase Map

| Phase | Focus | Backend Task | Frontend Task | Dependency Rule |
|---|---|---|---|---|
| 1 | Foundation | `TASK-0022` | `TASK-0026` | Must complete before Phase 2 |
| 2 | Orders + Receiving | `TASK-0023` | `TASK-0027` | Requires Phase 1 contracts |
| 3 | Outbound + Approvals | `TASK-0024` | `TASK-0028` | Requires Phase 1; can overlap late Phase 2 |
| 4 | Inventory + Reports + Identifier + Decommission | `TASK-0025` | `TASK-0029` | Requires Phases 1-3 |

---

## Detailed Execution Plan

## Phase 1: Foundation (Core)

### Backend (`TASK-0022`)

- Introduce schema foundations for:
  - unit-aware quantities (compatibility path from legacy `quantity_kg`),
  - article `has_batch` behavior,
  - normalized article categories,
  - supplier/supplier_code alignment,
  - canonical hardware-source identity fields.
- Keep backward compatibility while new API contracts are being adopted.
- Add migration/backfill notes and tests.

### Frontend (`TASK-0026`)

- Add i18n architecture and Croatian baseline copy (with diacritics).
- Add language switcher (`hr/en/de/hu`) in this wave.
- Introduce shared layout tokens and widen content area globally.
- Add tablet behavior baseline (tablet default flow centered on `Automatski unos`).

### Exit Criteria

- Backend migrations apply cleanly.
- Frontend build passes with i18n/layout foundation.
- No locked-rule conflicts.

---

## Phase 2: Orders + Receiving

### Backend (`TASK-0023`)

- Implement Orders domain (`orders`, `order_lines`) with unique order-number rules:
  - auto format `ORD-xxxx`,
  - manual number allowed but must remain globally unique.
- Receiving linkage:
  - required `delivery_note_number`,
  - optional `order_line_id`,
  - ad-hoc receiving without order (note required).
- Keep order lifecycle recalculation (`OPEN`/`CLOSED`) based on active lines fulfillment.

### Frontend (`TASK-0027`)

- Build `Narudžbe` module and sub-screens:
  - `Otvorene narudžbe`,
  - `Ulaz robe`,
  - `Zatvorene narudžbe`.
- Refactor Receive Stock screen to approved business UX (article number flow, conditional batch input, quantity label, embedded history).
- Remove standalone Receipt History and Batches navigation entry points.

### Exit Criteria

- Orders can be created/edited and close automatically when complete.
- Receiving supports both order-linked and ad-hoc flows.
- UI navigation reflects new module structure.

---

## Phase 3: Outbound + Approvals

### Backend (`TASK-0024`)

- Add outbound draft-group numbering (`Broj izlaza`) and group-level description.
- Support approvals daily grouping by `Europe/Berlin` day boundary.
- Aggregate rows only for same `article + batch`.
- Implement pre-approval edit semantics (overwrite pending values, no correction tx before approval).
- Prepare source identity mapping (`scale_id`, `scanner_id`, `station_id`, `source_label`).

### Frontend (`TASK-0028`)

- Refactor Draft Entry to `Automatski unos` UX.
- Refactor Bulk Entry screen into `Izlaz` workflow and new row structure.
- Rebuild Approvals UI into day-list + list-level actions (approve/reject/edit).

### Exit Criteria

- Approvals workflow is list-based per day and role-safe (ADMIN-only actions).
- Outbound UX uses new group model and no redundant fields.

---

## Phase 4: Inventory + Reports + Identifier + Cleanup

### Backend (`TASK-0025`)

- Inventory endpoints:
  - category filtering,
  - active/inactive/all,
  - article inspect payload with batch quantities and last activity fields.
- Reports backend:
  - inventory count list,
  - surplus list,
  - statistics baseline endpoints,
  - export endpoints for Excel/PDF where required.
- Article Identifikator backend:
  - alias lookup,
  - missing-article reporting queue with dedup and close/resolve actions.
- Decommission old endpoints/screens support as approved (including `/api/batches` standalone create path).

### Frontend (`TASK-0029`)

- Build consolidated `Skladište` screen replacing standalone `Articles` usage.
- Build `Izvještaji` sub-screens and remove raw transaction-table UI.
- Build `Article Identifikator` flows for OPERATOR + ADMIN.
- Complete decommission of old UI routes.

### Exit Criteria

- Legacy screens removed from navigation.
- New modules fully operational per RBAC rules.
- Documentation and migrations fully synchronized.

---

## Cross-Cutting Rules (Must Hold in Every Phase)

1. RBAC:
   - `ADMIN`: approvals, receiving, orders, reports, article master actions.
   - `OPERATOR`: draft create, inventory view, identifier lookup/report submit.
2. Time:
   - Persist timestamps in UTC.
   - Daily approvals grouping in `Europe/Berlin`.
3. Quantity model:
   - New work is unit-aware.
   - Legacy `quantity_kg` compatibility is transitional only.
4. Batch logic:
   - Driven by `has_batch`, not `is_paint`.
5. Audit:
   - Every stock-changing operation must create auditable transaction metadata.

---

## Risk Register and Mitigations

1. **Data migration risk (quantity model, article fields)**  
   Mitigation: additive migrations first, backfill scripts, compatibility reads/writes, staged deprecation.

2. **Frontend/backend contract drift across phases**  
   Mitigation: phase-specific API contracts in each task brief and strict dependency gates.

3. **RBAC regressions during module moves**  
   Mitigation: explicit ADMIN/OPERATOR acceptance checks in every phase.

4. **Decommission breaks hidden dependencies**  
   Mitigation: remove legacy routes only in Phase 4 after feature parity and verification.

---

## Verification Plan (Program Level)

### Backend

```bash
cd backend
pytest -v
```

### Frontend

```bash
cd desktop-ui
npm run build
```

### Mandatory Manual Regression

1. ADMIN and OPERATOR login + route visibility checks.
2. End-to-end receiving (with and without order).
3. End-to-end draft -> approval -> stock update.
4. Inventory inspect and category filters.
5. Reports exports (Excel/PDF) and statistics loading.
6. Article Identifikator lookup + missing report lifecycle.

---

## Deliverables

- Detailed phase task briefs:
  - Backend: `TASK-0022` .. `TASK-0025`
  - Frontend: `TASK-0026` .. `TASK-0029`
- Agent prompts:
  - backend prompt for phased execution
  - frontend prompt for phased execution
- Changelog entry documenting v3.0 planning kickoff.

---

## Definition of Done (v3.0 Planning)

Planning package is complete when:

1. All phase task briefs exist and are dependency-ordered.
2. Backend/frontend prompts reference correct docs and rules.
3. Changelog marks this as next-version implementation wave.
4. No unresolved contradiction remains between RULES, DECISIONS, and TASK briefs.
