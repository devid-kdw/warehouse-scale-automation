# TASK-0010: Core Backend Refinement (v2)

**Goal**: Implement strict data integrity for Transactions (order numbers), optimize Receipt history, and enforce Approval atomicity.

** Assigned to**: Backend Agent

---

## 1. Database & Models

### Transaction Table
- [ ] **Add Column**: `order_number` (Text, nullable).
- [ ] **Add Indexes**:
  - `ix_transactions_type_created` on `(tx_type, occurred_at)`
  - `ix_transactions_order_number` on `(order_number)`
- [ ] **Normalization**: Ensure `order_number` is always trimmed and uppercase before saving.

### Article Logic
- [ ] **Consumables Handling**:
  - If `article.is_paint == False`:
    - Logic must use a "System Batch" (Code=`NA`, Expiry=`2099-12-31`).
    - Ensure this batch is created idempotently (don't create duplicates).

### Draft Groups
- [ ] **Name Field**: Ensure `name` column is editable (already exists, verify PATCH support).

---

## 2. API Updates

### Receiving (`POST /api/inventory/receive`)
- [ ] **Validation**: `order_number` is now **REQUIRED**.
  - Return `400 Bad Request` if missing.
- [ ] **Processing**: Store normalized `order_number` in Transaction.

### Receipt History (`GET /api/inventory/receipts`)
- [ ] **New Endpoint**: Create an endpoint optimized for "Receipts" view.
- [ ] **Grouping Logic**:
  - Group `STOCK_RECEIPT` transactions by `order_number` + `client_event_id` (or tight time window if event_id missing).
- [ ] **Response Format**:
  ```json
  [
    {
      "receipt_key": "unique_group_id",
      "order_number": "ORD-2026-001",
      "received_at": "2026-02-07T10:00:00Z",
      "line_count": 5,
      "total_quantity": 150.50,
      "items": [...] // Optional: can be loaded via detail endpoint if preferred
    }
  ]
  ```

### Draft Groups
- [ ] **Update Name**: Implement `PATCH /api/draft-groups/{id}`.
- [ ] **Auto-Naming Logic**:
  - Format: `{Source}_{Counter}-{YYYY-MM-DD}`
  - Example: `AdminDraft_001-2026-02-07`
  - Logic: Count existing groups for Today + Source, increment by 1, pad with 00x.
- [ ] **Approval Atomicity (CRITICAL)**:
  - **Rule**: All-or-Nothing.
  - If pressing "Approve" on a group causes *any* line to fail (e.g. negative stock), **ROLLBACK EVERYTHING**.
  - Return `409 Conflict` with specific error message.
  - Group status remains `DRAFT`.

---

## 3. Verification Steps (Backend)

- [ ] Run `pytest` to verify `order_number` constraint (400 if missing).
- [ ] Run `pytest` to confirm atomicity (mock a failure and ensure no stock changed).
- [ ] Check DB migration generates correct indexes.
