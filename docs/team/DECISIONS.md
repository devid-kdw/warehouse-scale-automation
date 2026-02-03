# Decision Log

This document tracks all architectural and policy decisions for the Warehouse Scale Automation project.

Format: **Date** | **Decision** | **Rationale** | **Implications**

---

## Active Decisions

### 2026-02-03 - Single Location Policy (v1.x)
**Decision**: Location is fixed to ID=1, code="13" for all v1.x releases.

**Rationale**: Simplifies implementation and UI. Multi-location support is not needed for initial warehouse deployment. Reduces complexity in inventory queries and draft creation.

**Implications**:
- UI does not show location selector (hardcoded)
- API still accepts `location_id` parameter for future compatibility
- All seed data must create location with code="13"
- Backend validates location existence but assumes single location

---

### 2026-02-03 - Batch Expiry Required
**Decision**: `expiry_date` is REQUIRED for all batches in paint domain.

**Rationale**: Paint products have shelf life. Operating without expiry tracking leads to use of expired materials. Visual warnings (red/orange badges) are critical for warehouse safety.

**Implications**:
- Backend validation: 400 error if `expiry_date` is NULL on batch creation
- Frontend: expiry date picker is required field (marked with *)
- Receiving workflow must enforce expiry input
- UI displays color-coded expiry warnings:
  - 🔴 Red: Expired (`expiry_date < today`)
  - 🟠 Orange: Expiring soon (`< 30 days`)
  - ⚪ Gray: OK (`> 30 days`)

---

### 2026-02-03 - Batch Expiry Mismatch Policy
**Decision**: If a batch already exists with an expiry date, receiving with a different expiry date returns **409 CONFLICT** error.

**Rationale**: Silently overwriting expiry dates can cause chaos. Same batch code should represent same physical batch with same expiry. Different expiry = different batch code.

**Implications**:
- Receiving API must validate expiry match when batch exists
- Error response: `BATCH_EXPIRY_MISMATCH` with existing and provided expiry
- Admin must explicitly handle mismatches (cannot be automatic)

---

### 2026-02-03 - Inventory Count Shortage Handling
**Decision**: When inventory count shows a shortage (counted < total):
1. `surplus` is reset to 0
2. Deficit creates a `WeighInDraft` with `draft_type=INVENTORY_SHORTAGE`
3. Admin must approve the draft to reduce stock
4. Stock never goes below 0 automatically

**Rationale**: Ensures audit trail for all stock reductions. Prevents accidental negative inventory. Requires admin approval for discrepancies.

**Implications**:
- Shortage drafts go through approval workflow
- Stock remains unchanged until draft approved
- Transaction trail shows: count adjustment + shortage draft approval
- UI must clearly indicate "pending shortage approval"

---

### 2026-02-03 - Inventory Count Surplus Handling
**Decision**: When inventory count shows surplus (counted > total):
1. Difference is added to `surplus` table
2. `stock` remains unchanged
3. Transaction recorded as `INVENTORY_ADJUSTMENT` targeting surplus

**Rationale**: Surplus represents overage that will be consumed first. Stock remains accurate to what was received. Surplus auto-consumes before stock in approval workflow.

**Implications**:
- No manual approval needed for surplus increase
- Surplus visible in inventory summary
- Next consumption will use surplus-first logic

---

### 2026-02-03 - Role-Based Access Control (RBAC)
**Decision**: Two roles with distinct permissions:
- **OPERATOR**: Can only create drafts (weigh-in)
- **ADMIN**: Full access (drafts, approvals, inventory, reports, batches, articles, receiving)

**Rationale**: Separation of duties. Operators perform daily weighing tasks. Admins handle approvals, inventory management, and system configuration.

**Implications**:
- Frontend routes protected with `RequireAuth` and `RequireAdmin` wrappers
- Backend endpoints decorated with `@require_roles('ADMIN')`
- JWT tokens include `role` claim
- Receiving workflow is ADMIN-only (operators cannot add stock)

---

### 2026-02-03 - Receiving Increases STOCK Only
**Decision**: Receiving workflow increases `stock.quantity_kg`, never `surplus`.

**Rationale**: Surplus represents overage from inventory counts, not received goods. Stock is what was officially received. Clear separation prevents confusion.

**Implications**:
- `POST /api/inventory/receive` updates stock table only
- Transaction type: `STOCK_RECEIPT` (not WEIGH_IN)
- Operators have no access to receiving (ADMIN-only)

---

### 2026-02-03 - Transaction History Default: 90 Days
**Decision**: UI defaults to showing last 90 days of transactions. Backend allows unlimited range with query params.

**Rationale**: Balance between usability and performance. Most operational queries look at recent history. Longer ranges available via date picker.

**Implications**:
- Frontend automatically sets `start_date = today - 90 days`
- Backend `GET /api/reports/transactions` accepts optional `start_date` and `end_date`
- Full history available but requires explicit date range selection

---

### 2026-02-03 - Orchestration Documentation Structure
**Decision**: Establish `docs/team/`, `docs/status/`, `docs/tasks/` structure with mandatory changelog, decision log, and status reports.

**Rationale**: Clear project history and decision tracking. Enables Stefan to always know what changed, why, and what's next. Facilitates agent coordination.

**Implications**:
- All changes logged in `CHANGELOG.md`
- All architectural decisions logged in `DECISIONS.md`
- Weekly status reports in `docs/status/YYYY-MM-DD.md`
- Task briefs in `docs/tasks/TASK-XXX-name.md`
- Orchestrator responsible for maintaining these documents

---

## Deprecated/Superseded Decisions

_(None yet)_
