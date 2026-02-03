# Rules of Engagement

**Status**: 🔒 LOCKED  
**Last Updated**: 2026-02-03

These rules are **LOCKED** and cannot be changed without explicit approval. All agents must adhere to these constraints.

---

## 🔒 Business Logic Rules

### 1. Transaction Sign Convention

**Rule**: Transactions represent **inventory changes**, not accounting debits/credits.

- **Consumption** (WEIGH_IN, STOCK_CONSUMED, SURPLUS_CONSUMED): **Negative** quantity
- **Receipt/Additions** (RECEIPT, INVENTORY_ADJUSTMENT with increase): **Positive** quantity
- Transaction `quantity_kg` in database stores algebraic value (can be positive or negative)

**Rationale**: Matches physical inventory movement; consumption reduces stock.

---

### 2. Surplus-First Consumption

**Rule**: When approving WEIGH_IN drafts, **surplus is consumed before stock**.

**Logic**:
1. Check if surplus exists for (location, article, batch)
2. If surplus ≥ needed → consume from surplus only
3. If surplus < needed → consume all surplus, then consume remainder from stock
4. If insufficient stock → reject draft with error

**Rationale**: Surplus represents "buffer" from previous inventory adjustments; should be used first.

**Implementation**: See `backend/app/services/approval_service.py`

---

### 3. Location Fixed = 13

**Rule**: Location is **hardcoded to 13** in v1. No multi-location support.

- UI should not show location selector
- API can accept `location_id`, but v1 clients always send `13`
- Database schema supports multiple locations (future-ready), but business logic assumes single location

**Rationale**: Simplicity for initial deployment; avoid complexity until multi-site expansion.

---

### 4. Batch Code Validation

**Rule**: Batch codes must match one of two formats:

- **Mankiewicz**: Exactly **4 or 5 digits** (e.g., `0606`, `12345`)
- **Akzo Nobel**: **9 to 12 digits** (e.g., `123456789`, `123456789012`)

**Regex**: `^\d{4,5}$|^\d{9,12}$`

**Rationale**: Supplier-specific formats; validation prevents typos during manual entry.

**Implementation**: See `backend/app/services/validation.py`

---

### 5. Article Aliases

**Rule**: Aliases are **lookup-only** shortcuts for finding articles.

- Maximum **5 aliases** per article
- Aliases must be **globally unique** (cannot point to multiple articles)
- Aliases cannot be used as primary identifiers in database foreign keys
- Search endpoints accept aliases, but responses always return canonical `article_code`

**Rationale**: User convenience (e.g., `"RAL9005"` → finds article `800147`), but avoids data integrity issues.

**Implementation**: See `backend/app/models/article_alias.py`

---

### 6. Stock Never Goes Below Zero

**Rule**: Stock quantities **cannot be negative**.

- Database constraint: `CHECK (quantity_kg >= 0)` on `stock` table
- Approval service must validate sufficient stock before approving consumption drafts
- If stock would go negative → draft is **rejected** with error `ERR_INSUFFICIENT_STOCK`

**Rationale**: Physical inventory cannot be negative; prevents data corruption.

---

### 7. Inventory Shortage Handling

**Rule**: When inventory count reveals a **shortage** (physical < system), create a **draft** for admin approval, not immediate adjustment.

**Process**:
1. Operator performs physical inventory count
2. System calculates difference: `system_stock - physical_count`
3. If difference > 0 (shortage):
   - Create draft with `draft_type = INVENTORY_SHORTAGE`
   - Admin must review and approve
   - Upon approval → stock reduced, transaction created with audit trail
4. If difference < 0 (surplus):
   - Automatically add to `surplus` table (no approval needed)
   - If surplus already exists, overwrite previous surplus

**Rationale**: Shortages require investigation; surplus is expected variance and auto-tracked.

**Implementation**: See `backend/app/services/inventory_service.py`

---

### 8. JWT Secret Production Fail-Safe

**Rule**: Application **must not start** in production mode with default/development JWT secret.

**Validation** (in `backend/app/config.py`):
```python
if ENV == 'production' and JWT_SECRET_KEY == 'dev-secret-change-me':
    raise ValueError("Cannot use default JWT secret in production!")
```

**Rationale**: Prevent security breach from forgotten configuration.

---

## 🚨 Concurrency & Data Integrity

### 9. Row-Level Locking for Approvals

**Rule**: Approval service must use **FOR UPDATE** locking when modifying stock/surplus.

```python
stock = db.session.query(Stock).filter_by(...).with_for_update().first()
```

**Rationale**: Prevents race conditions when multiple admins approve drafts simultaneously.

**Implementation**: See `backend/app/services/approval_service.py`

---

### 10. Idempotency via `client_event_id`

**Rule**: API endpoints that create transactions should accept optional `client_event_id`.

- If provided, `client_event_id` must be **unique** (database constraint)
- Duplicate `client_event_id` → return existing transaction (idempotent)
- Prevents duplicate transactions from network retries

**Rationale**: Mobile/desktop clients may retry requests; prevents accidental double-entries.

---

## 📊 Audit Trail Requirements

### 11. All Inventory Changes Must Be Logged

**Rule**: Every change to stock/surplus **must** create a `Transaction` record.

**Required fields**:
- `tx_type`: WEIGH_IN, SURPLUS_CONSUMED, STOCK_CONSUMED, INVENTORY_ADJUSTMENT, RECEIPT
- `occurred_at`: UTC timestamp
- `quantity_kg`: Algebraic change (positive = addition, negative = consumption)
- `user_id`: Who performed the action
- `meta`: JSON with additional context (e.g., `{"draft_id": 123, "approval_action_id": 456}`)

**Rationale**: Complete audit trail for compliance, troubleshooting, and reporting.

---

## 🔐 Security & Authentication

### 12. Role-Based Access Control

**Rule**: Two roles only: **ADMIN** and **OPERATOR**.

| Action | OPERATOR | ADMIN |
|--------|----------|-------|
| Create drafts | ✅ | ✅ |
| Approve/reject drafts | ❌ | ✅ |
| View inventory | ✅ | ✅ |
| Manage articles/batches | ❌ | ✅ |
| View reports | ❌ | ✅ |
| Manage users | ❌ | ✅ |

**Implementation**: JWT contains `role` claim; endpoints check `@jwt_required()` + role validation.

---

## 🛑 Change Control

### How to Modify Locked Rules

1. **Document the reason** for change (business requirement, bug fix, architecture improvement)
2. **Get explicit approval** from project owner (Stefan)
3. **Update this document** with new rule version and rationale
4. **Create migration plan** if existing data/code is affected
5. **Update all affected tests** and documentation

**Do NOT** modify these rules without following this process.

---

## 📝 Version History

| Date | Rule Changed | Reason | Approved By |
|------|--------------|--------|-------------|
| 2026-02-03 | Initial version | Project setup | Stefan |

