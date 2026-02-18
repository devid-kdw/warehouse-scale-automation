# Task Brief: TASK-0027 — Frontend v3 Phase 2 (Orders & Receiving UI)

**Created**: 2026-02-17  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Implement the new `Narudžbe` module and receiving UX aligned with backend Orders/Receiving contracts.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/frontend-agent-tasks/TASK-0026-frontend-v3-phase-1-shell-i18n-layout.md`
3. `docs/tasks/backend-agent-tasks/TASK-0023-backend-v3-phase-2-orders-and-receiving.md`
4. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-003`, `S-004`, `S-008`, `S-010`)
5. `docs/team/RULES_OF_ENGAGEMENT.md` (RBAC + receiving rules)
6. `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
7. `docs/tasks/backend-agent-tasks/TASK-0026B-backend-runtime-contract-stabilization.md`

---

## Backend Gate (Current)

Per latest backend audit and TASK-0026B, receiving and receipt-history contracts are stabilized for frontend integration.
Frontend should integrate directly against current API contracts (no blocked-mode stubs required for this phase).

---

## Scope

### In Scope

- Create module `Narudžbe` with sub-screens:
  - `Otvorene narudžbe`
  - `Ulaz robe`
  - `Zatvorene narudžbe`
- Receive Stock UI refactor:
  - title -> `Ulaz robe`,
  - remove old subtitle text,
  - article number input + separate article name display,
  - `Ima šaržu` indicator bound to article `has_batch` (not user override),
  - expiry grouped with batch semantics,
  - quantity label without KG suffix,
  - keep note field.
- Integrate order-line receiving support and delivery note capture.
- Embed receipt history list inside `Ulaz robe` screen.
- Remove standalone `Receipt History` and `Batches` screen entry points from navigation.

### Out of Scope

- Draft/Approvals redesign (Phase 3).
- Inventory/Reports/Identifier redesign (Phase 4).

---

## Technical Changes

### 1) Orders UI

- Order header supports:
  - auto/manual order number,
  - supplier code,
  - supplier/manufacturer,
  - list of order lines (article number, quantity, UOM, delivery date).
- Open/closed order lists with clear received-state visuals.

### 2) Receiving UI (`Ulaz robe`)

- Build receive form against new backend contract (`delivery_note_number`, optional `order_line_id`).
- Support ad-hoc receiving flow with note.
- Keep batch behavior conditional based on article `has_batch`.
- Route and payload alignment:
  - endpoint: `POST /api/inventory/receive`
  - always send `article_id`, `delivery_note_number`, `quantity`, `uom`
  - if `order_line_id` is omitted, enforce mandatory `note` in UI
  - for non-batch articles send empty batch/expiry and let backend apply system defaults
  - do not call deprecated `POST /api/batches` from new flows
- Conversion boundary alignment:
  - stock-changing flows currently support `KG` and `L`
  - show blocking validation message for unsupported UOM in receive actions

### 3) Navigation and IA

- Introduce Orders parent node with 3 child screens.
- Remove legacy standalone routes from sidebar once parity exists.
- Keep backend receipt history integration via existing endpoint (`GET /api/inventory/receipts`) until dedicated orders-history contract replaces it.

---

## Acceptance Criteria

1. [ ] `Narudžbe` module with 3 sub-screens is accessible to ADMIN.
2. [ ] `Ulaz robe` screen follows approved UX labels and conditional batch behavior.
3. [ ] Order-linked and ad-hoc receiving UI flow is complete against current backend APIs.
4. [ ] Receipt history panel is integrated in receiving flow using current backend endpoint.
5. [ ] `Receipt History` and `Batches` no longer appear as standalone navigation screens.
6. [ ] Build passes and route guards remain RBAC-safe.
7. [ ] Receiving form enforces backend-required `note` for ad-hoc flow and does not use deprecated batch-create endpoint.

---

## Test Plan

### Automated

```bash
cd desktop-ui
npm run build
```

### Manual

1. Create order with multiple lines and delivery dates.
2. Receive partial lines and confirm order remains open.
3. Receive remaining lines and confirm order moves to closed.
4. Verify receipt history is visible within receiving screen and data is grouped correctly.
5. Verify standalone receipt history/batches screens are not in sidebar.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`

---

## Status Updates

- 2026-02-17: Task created.
