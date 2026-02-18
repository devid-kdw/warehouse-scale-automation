# Decision Log

This document tracks architectural and policy decisions.

---

## Active Decisions

### 2026-02-03 - Single Location Policy (v1)
**Decision**: Location is fixed to ID=13 in v1 workflows.  
**Implications**:
- UI does not expose location selector in v1.
- API can still accept `location_id` for forward compatibility.

### 2026-02-03 - Inventory Integrity Baseline
**Decision**:
- Surplus-first consumption is mandatory.
- Stock cannot go negative.
- Shortage from inventory count creates approval draft.
- Surplus from inventory count is auto-added to surplus bucket.

### 2026-02-03 - Receiving Boundary
**Decision**: Receiving increases stock only (not surplus) and is ADMIN-only.

### 2026-02-03 - Batch Expiry Mismatch
**Decision**: Existing batch with different expiry on receive returns 409 (`BATCH_EXPIRY_MISMATCH`).

### 2026-02-12 - RBAC Clarification: OPERATOR Inventory View
**Decision**: OPERATOR can view inventory summary; reports/admin operations remain restricted.

### 2026-02-17 - Croatian-First UI + i18n Direction
**Decision**:
- UI copy baseline is Croatian.
- Code identifiers and API contracts stay in English.
- i18n architecture must support `hr`, `en`, `de`, `hu`.

### 2026-02-17 - Global Layout Width Direction
**Decision**: Screen content areas should be widened (responsive) to reduce wasted space and improve input readability.

### 2026-02-17 - Multi-Unit Semantics (Major Refactor Approved)
**Decision**:
- System direction is unit-aware quantities (not KG-only UX/contract semantics).
- Existing `quantity_kg` data must be migrated without losing audit history.

### 2026-02-17 - Batch Logic Generalization
**Decision**:
- Batch behavior is driven by article-level `has_batch`/`is_batch_tracked` semantics.
- `is_paint` is no longer the rule trigger for required batch/expiry.

### 2026-02-17 - Bulk Entry Domain Rename and Model Direction
**Decision**:
- `Bulk Entry` operationally becomes `Izlaz`.
- Outbound reference requires dedicated system field (`receipt_number`) with migration/sequence.
- Existing test data can be reset to simplify migration rollout.

### 2026-02-17 - Receiving IA Consolidation
**Decision**:
- `Receipt History` standalone screen is removed.
- Receipt history is embedded in `Ulaz robe`.

### 2026-02-17 - Inventory Module Consolidation
**Decision**:
- `Inventory` becomes `Skladiste`/`Pregled artikala` UX.
- Standalone `/articles` and `/batches` UIs are decommission targets.
- Admin article functions migrate into inventory module.

### 2026-02-17 - Reports Module Refactor
**Decision**:
- Reports module (`Izvjestaji`) shifts from raw transaction table focus to:
  - `Inventurna lista`
  - `Surplus lista`
  - `Statistike`
- Inventory list rows are `article + batch`.
- Reorder yellow zone is defined as `threshold < qty <= threshold * 1.10`.

### 2026-02-17 - Approvals Aggregation Rule
**Decision**:
- Daily aggregation allowed only for same `article + batch`.
- Same article in different batches remains separate rows.

### 2026-02-17 - Orders Module (Narudzbe) Approved
**Decision**:
- New module with sub-screens:
  - `Otvorene narudzbe`
  - `Ulaz robe`
  - `Zatvorene narudzbe`
- `Order` + `OrderLine` model is required.
- `order_number` can be auto-generated or manual; both must be unique.
- Per-line `delivery_date` is required business field.
- Receiving line captures `delivery_note_number`; optional `order_line_id` linkage.
- Receiving without order is allowed with explanatory note.
- Order closes when all active lines are fulfilled.

### 2026-02-17 - Article Identifikator Module Approved
**Decision**:
- New shared module for ADMIN + OPERATOR lookup by alias/text/code.
- If no match exists, user can submit missing-article report.
- Admin has queue to process reports (status workflow + notes).

### 2026-02-17 - Implementation Clarifications (Owner Follow-up)
**Decision**:
- Language switcher (`hr/en/de/hu`) is included in current implementation wave.
- Layout standardization is required across screens with reduced side gutters and wider content area.
- Draft Entry keeps `scale` as first-load default.
- UOM strategy is open entry + persistent catalog growth (new unit is saved and reusable).
- Approvals day grouping: operational day is `Europe/Berlin`; timestamp storage remains UTC.
- Pre-approval aggregate edits overwrite pending draft values; no correction transaction pre-approval.
- Hardware identity schema should be standardized now (`scale_id`, `scanner_id`, `station_id`, `source_label`, extensible metadata).
- Identifier report queue is hosted under Reports module (`Izvještaji`) as dedicated sub-view.
- Identifier reports are deduplicated by normalized input and closed only by explicit admin close action.
- Statistics v1 should include all proposed baseline options; avoid split lists by UOM.
- Auto order number format is `ORD-xxxx` (numeric padded).

### 2026-02-17 - Backend Contract Alignment After v3 Backend Wave
**Decision**:
- Frontend implementation must align to as-implemented backend contracts, not only planned contracts.
- Canonical admin Identifikator routes are `/api/admin/identifikator/*`; legacy `/api/identifikator/admin/*` is temporary fallback.
- Standalone batch creation and transaction-table report APIs remain deprecated fallback and are excluded from new UI flows.
- Full `quantity_kg` removal is deferred to dedicated decommission/remediation task (`TASK-0026A`), while frontend uses unit-aware fields where available and compatibility mapping where necessary.

---

## Superseded / Deprecated Decisions

### Superseded by 2026-02-12 RBAC Clarification
- 2026-02-03 statement: "OPERATOR can only create drafts".

### Superseded by 2026-02-17 Batch Logic Generalization
- Paint-coupled rule where non-paint always maps to system batch as universal behavior.

### Planned Deprecation (Owner Decision 2026-02-17)
- `POST /api/batches` standalone creation endpoint after migration to receiving-only batch creation flow.

---

## Notes

- For implementation input and screen-by-screen business details, see:
  - `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
