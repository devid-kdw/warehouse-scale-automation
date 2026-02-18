# Orchestrator Backend Audit - 2026-02-17 (Final Sync)

**Scope**: Post-remediation backend contract recheck for frontend handoff  
**Reviewer**: Orchestrator  
**Status**: Green for frontend integration

---

## 1) Backend Delivery Status

### Confirmed Implemented
- v3 foundations: `has_batch`, `supplier_code`, `category`, `density`, UOM catalog.
- Orders domain: `orders`, `order_lines`, auto/manual order numbering.
- Outbound + approvals daily workflow.
- Inventory consolidation (`Article+Batch`) + inspect contract.
- Reports v3 modules and exports.
- Identifikator with canonical admin routes.
- Unit-aware model contract: canonical `quantity` + `uom`.

### Migrations Present
- `v3_phase1_foundation`
- `v3_phase2_orders`
- `v3_phase3_approvals`
- `ad7df8209648_v3_phase4_inventory_reports`
- `v3_p4_remed`
- `v3_p4_decom`

---

## 2) Contract Readiness for Frontend

### Canonical Contracts (Use in New UI)
- `quantity` + `uom` across inventory, drafts, approvals, transactions, reports.
- Receiving:
  - `POST /api/inventory/receive`
  - `GET /api/inventory/receipts`
- Draft daily approvals:
  - `GET /api/drafts/daily`
  - `GET /api/drafts/daily/<date>/<location_id>`
  - `POST /api/drafts/daily/<date>/<location_id>/approve|reject`
  - `PATCH /api/drafts/daily/<date>/<location_id>/lines`
- Inventory:
  - `GET /api/inventory`
  - `GET /api/inventory/<article_id>/inspect`
- Orders:
  - `/api/orders*`
- Reports:
  - `inventurna`, `surplus`, `statistics/*` endpoints
- Identifikator:
  - canonical admin routes `/api/admin/identifikator/*`

### Legacy/Fallback (Do Not Use for New UI)
- `/api/identifikator/admin/*` (fallback only; deprecated headers present)
- `/api/reports/transactions` (legacy fallback only)
- `/api/batches` create path (deprecated; receiving flow is canonical)

---

## 3) Residual Notes (Non-blocking for Frontend)

- Some SQLite-only test behaviors differ from PostgreSQL for:
  - partial unique index behavior in missing-article dedup tests,
  - synthetic thread-concurrency tests around receipt numbering.
- These are not frontend blockers and do not change canonical API usage.

---

## 4) Frontend Guidance

1. Frontend can start full phase integration (no backend-hotfix gate required).
2. Use canonical `quantity` + `uom` fields in all new UI models.
3. Keep deprecated endpoints out of primary flows.
4. If any runtime mismatch is discovered, report endpoint + payload delta + affected UI file.
