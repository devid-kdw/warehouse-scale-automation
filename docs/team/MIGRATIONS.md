# Database Migrations Log

Tracks applied and planned schema migrations.

---

## Applied Migrations

### `c1d4f113222c_initial_migration.py`
- Initial core schema.

### `f11e5d13d9f6_add_password_hash_to_users.py`
- Added `users.password_hash`.

### `add_draft_groups_manual.py`
- Added `draft_groups` and backfilled `weigh_in_drafts.draft_group_id`.

### `a3f5e8b2c1d4_add_article_expansion_aliases_draft_type.py`
- Added alias table and draft type expansion.

### `c8f64cf6440c_add_order_number_and_indexes.py`
- Added `transactions.order_number` and related indexes.

### `v3_phase1_foundation.py`
- TASK-0022: v3 Phase 1 Foundation (Completed 2026-02-17)

### `v3_phase2_orders.py`
- TASK-0023: v3 Phase 2 Orders & Receiving (Completed 2026-02-17)
- `orders` and `order_lines` tables
- FK constraint: `transactions.order_line_id` -> `order_lines.id`
- Order number uniqueness (DB level)

### `v3_phase3_approvals_v3_phase3_approvals.py`
- TASK-0024: v3 Phase 3 Outbound & Approvals (Completed 2026-02-17)
- Added `draft_groups.receipt_number` and `draft_groups.description` (+ backfill)

### `v3_p4_remed_v3_phase4_remediation.py`
- TASK-0026: v3 Phase 4 Remediation & Polish (Completed 2026-02-17)
- Added `articles.density` (default 1.0)
- Enforced `NOT NULL` on `transactions.quantity` and `transactions.uom`
- Historical backfill: `quantity = quantity_kg, uom = 'KG'`

### `ad7df8209648_v3_phase4_inventory_reports.py`
- TASK-0025: v3 Phase 4 Inventory/Reports/Identifier foundations (Completed 2026-02-17)
- Added `missing_article_reports` table.

### `v3_p4_decom.py`
- Draft migration prepared for dropping `quantity_kg` columns.
- Not promoted to stable rollout yet because runtime/service contracts still reference legacy KG fields.
- Full decommission execution is tracked in `TASK-0026A`.

---

## Planned Migration Wave (TASK-0020 Alignment)

The following schema changes are expected and must be implemented in coordinated backend tasks:

1. ✅ ~~Unit-aware quantity model migration~~ (done in v3_phase1_foundation)
2. ✅ ~~Article batch-tracking field (`has_batch`)~~ (done in v3_phase1_foundation)
3. ✅ ~~Orders domain~~ (done in v3_phase2_orders)
4. ✅ ~~Receiving linkage additions~~ (done in v3_phase2_orders)
5. ✅ ~~Missing article reporting entity~~ (done in v3_phase4_inventory_reports)
6. ✅ ~~Deprecation/removal path for standalone batch create~~ (Headers added in Phase 2)
7. Legacy `quantity_kg` full decommission migration + contract cleanup (`TASK-0026A`).

---

## Migration Standards

- Every migration must include rollback path when feasible.
- Data migrations must preserve audit integrity.
- Migration notes must describe production impact, downtime risk, and backfill strategy.
- Update `CHANGELOG.md` and task brief upon migration completion.

---

Last Updated: 2026-02-17
