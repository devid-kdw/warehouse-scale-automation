# Rules of Engagement

**Status**: LOCKED  
**Last Updated**: 2026-02-17

These rules are LOCKED and cannot be changed without explicit project owner approval.

---

## 1. Transaction Sign Convention

Transactions represent physical inventory movement.

- Consumption (`WEIGH_IN`, `STOCK_CONSUMED`, `SURPLUS_CONSUMED`) is negative.
- Additions (`STOCK_RECEIPT`, positive `INVENTORY_ADJUSTMENT`) are positive.
- Legacy persistence still uses `quantity_kg`; transition target is unit-aware quantity model.

## 2. Unit-Aware Quantity Direction (Approved, Mandatory for New Work)

- New UI and API work must be unit-aware, not KG-only.
- Article UOM is authoritative for operational entry and display.
- Migration from `quantity_kg`-centric model must preserve audit/history integrity.
- Current stock-changing backend runtime supports only `KG` and `L` conversions.
- Unsupported stock-changing UOM conversions must return `UNSUPPORTED_UOM_CONVERSION` (400).

## 3. Surplus-First Consumption

When approving consumption drafts:
1. Consume surplus first.
2. Consume stock second.
3. Reject if stock is insufficient.

## 4. Location Fixed = 13 (v1)

- UI does not expose location selector in v1.
- API may accept `location_id`, but v1 clients send `13`.

## 5. Batch Code Validation

Batch code regex remains:
- `^\d{4,5}$|^\d{9,12}$`

## 6. Batch Tracking Policy (Supersedes Paint-Coupled Rule)

- Batch requirement is controlled by article master flag (`has_batch` / `is_batch_tracked`).
- `is_paint` is classification only and must not drive mandatory batch logic.
- If article is batch-tracked, batch + expiry rules apply.

## 7. Batch Expiry Mismatch Protection

If existing batch expiry differs from provided expiry on receive, return `BATCH_EXPIRY_MISMATCH` (409).

## 8. Stock Never Goes Below Zero

- Stock cannot become negative.
- Approval and adjustment workflows must validate before write.

## 9. Inventory Count Discrepancy Handling

- If counted > system total: add difference to surplus.
- If counted = system total: no change.
- If counted < system total: create shortage draft for admin approval.

## 10. Receiving Workflow Boundaries

- Stock additions happen only through receiving workflow (or approved inventory-count pathways).
- Receiving remains ADMIN-only.
- Receiving may be linked to order line (`order_line_id`) or ad-hoc without order.

## 11. Orders + Receiving Linkage

- `delivery_note_number` is required for receiving traceability.
- `order_line_id` is optional and used when receiving against an open order line.
- Ad-hoc receiving (without order) is allowed and must include explanatory note.

## 12. Order Lifecycle

- Orders are `OPEN` until all active lines are fully received.
- Order moves to `CLOSED` automatically when all active lines are fulfilled.
- Admin can edit/remove unresolved lines; status must be recalculated immediately.

## 13. Idempotency via `client_event_id`

- Create endpoints may accept `client_event_id`.
- Duplicates must be handled idempotently.

## 14. Audit Trail Is Mandatory

Every inventory-changing operation must create transaction audit entry.

Required minimum fields:
- `tx_type`
- `occurred_at` (UTC)
- algebraic quantity change
- `user_id`
- context metadata (`meta`)

When applicable, include:
- `order_number`
- `order_line_id`
- `delivery_note_number`

## 15. RBAC

Only two roles exist: `ADMIN`, `OPERATOR`.

| Action | OPERATOR | ADMIN |
|---|---|---|
| Create drafts | YES | YES |
| Approve/reject drafts | NO | YES |
| View inventory | YES | YES |
| Receive stock | NO | YES |
| Manage orders | NO | YES |
| Manage article master data | NO | YES |
| Manage aliases | NO | YES |
| Use Article Identifikator lookup | YES | YES |
| Submit missing-article report | YES | YES |
| Process missing-article reports | NO | YES |
| View reports | NO | YES |
| Manage users | NO | YES |

## 16. Security Fail-Safe

Application must not start in production with default/weak JWT secret.

## 17. Concurrency

Inventory-changing approval/receiving flows must use row-level locking where required.

## 18. Timezone Semantics

- Persist timestamps in UTC.
- For daily approvals grouping, use operational timezone `Europe/Berlin` (Hamburg context in current deployment).
- Future versions should support location-driven timezone configuration.

## 19. Backend Contract Stability and Deprecation Policy (v3)

- Canonical Admin Identifikator API path is `/api/admin/identifikator/*`.
- Legacy Admin Identifikator fallback path `/api/identifikator/admin/*` remains temporarily available with deprecation headers.
- Standalone batch create endpoint `POST /api/batches` is deprecated and must not be used by new frontend flows.
- Legacy transaction report endpoint `/api/reports/transactions` remains fallback-only and must not be used for new report UX.

## 20. Transitional Quantity Compatibility Boundary

- Backend may still expose legacy KG fields in some read contracts during transition.
- New frontend work must prefer unit-aware fields (`quantity`, `uom`) when available.
- Any feature that requires full removal of `quantity_kg` must wait for dedicated decommission task completion.

---

## Change Control

To modify locked rules:
1. Record business reason.
2. Get explicit owner approval.
3. Update this file + `DECISIONS.md`.
4. Define migration/test/documentation impact.

---

## Version History

| Date | Rule Change | Reason | Approved By |
|---|---|---|---|
| 2026-02-03 | Initial locked rules | Initial project baseline | Stefan |
| 2026-02-17 | Unit-aware direction, has_batch policy, Orders/Receiving linkage, updated RBAC matrix | TASK-0020 owner feedback consolidation | Stefan |
| 2026-02-17 | Added v3 contract stability/deprecation and transitional quantity boundary rules | Backend implementation alignment and frontend contract safety | Stefan |
