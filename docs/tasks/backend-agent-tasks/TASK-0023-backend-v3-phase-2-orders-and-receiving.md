# Task Brief: TASK-0023 — Backend v3 Phase 2 (Orders & Receiving)

**Created**: 2026-02-17  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Implement Orders domain and receiving linkage rules so inbound workflow is fully traceable and aligned with approved v3 business logic.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/backend-agent-tasks/TASK-0022-backend-v3-phase-1-foundation-and-migrations.md`
3. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-003`, `S-004`, `S-008`, `S-010`)
4. `docs/team/RULES_OF_ENGAGEMENT.md` (Rules 10, 11, 12, 14, 15)
5. `docs/team/DECISIONS.md`

---

## Scope

### In Scope

- Implement `orders` and `order_lines` backend domain.
- Support order number policy:
  - auto-generated: `ORD-xxxx` (padded numeric),
  - manual input allowed,
  - global uniqueness for both.
- Add per-line `delivery_date` support.
- Extend receiving contract:
  - required `delivery_note_number`,
  - optional `order_line_id`,
  - ad-hoc receiving allowed with mandatory explanatory note.
- Recalculate order status (`OPEN`/`CLOSED`) after line receive/edit/remove.
- Prepare deprecation path for standalone `/api/batches` create flow.

### Out of Scope

- Approvals aggregation and daily list workflow (Phase 3).
- Reports and statistics refactor (Phase 4).

---

## Technical Changes

### 1) Orders Model and API

- Introduce order entities:
  - `Order`
  - `OrderLine`
- Required fields:
  - header: `order_number`, supplier reference/code/name, note, status,
  - line: `article_id`, ordered quantity, UOM, `delivery_date`, received quantity, line status.
- Endpoints:
  - create order,
  - edit order + line set,
  - list open orders,
  - list closed orders,
  - order detail.

### 2) Receiving Linkage Contract

- Receiving payload must carry:
  - `delivery_note_number` (required),
  - optional `order_line_id`,
  - ad-hoc mode note when `order_line_id` not provided.
- Ensure one delivery note can appear on multiple receipts and across orders.

### 3) Order Lifecycle Automation

- Auto-close order when all active lines are fully received.
- Reopen if admin edits lines into unfulfilled state.
- If admin removes unresolved lines, recalculate and close when applicable.

### 4) Batches Standalone Endpoint Deprecation Path

- Mark `/api/batches` standalone creation as deprecated in API docs.
- Keep temporary compatibility only if still needed by old clients during migration window.
- Add explicit removal note for Phase 4.

---

## Acceptance Criteria

1. [ ] Orders CRUD/list endpoints exist and enforce unique order numbers.
2. [ ] Auto order number format is `ORD-xxxx`.
3. [ ] Receiving validates `delivery_note_number` and supports optional `order_line_id`.
4. [ ] Receiving without order requires note and succeeds.
5. [ ] Order `OPEN/CLOSED` state recalculates correctly after receive/edit/remove.
6. [ ] API docs indicate `/api/batches` standalone create deprecation plan.

---

## Test Plan

### Automated

```bash
cd backend
pytest -v
```

### Focused

```bash
pytest tests/test_orders.py -v
pytest tests/test_receiving.py -v
pytest tests/test_inventory_receipts.py -v
```

### Manual Contract Checks

1. Create order (manual number) -> second same number must fail.
2. Create order (auto number) -> returns `ORD-xxxx`.
3. Receive against order line with delivery note -> line received qty increases.
4. Ad-hoc receive without order_line_id but with note -> success.
5. Verify order closes only when all active lines fulfilled.

---

## Rollout / Migration Notes

- Endpoint additions should be non-breaking to existing clients.
- Keep compatibility adapters until frontend modules are migrated in Phase 2.
- Final removal of deprecated batch-create path handled in Phase 4.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`
- [ ] `docs/team/MIGRATIONS.md` (if schema changes added)
- [ ] OpenAPI endpoint docs

---

## Status Updates

- 2026-02-17: Task created.

