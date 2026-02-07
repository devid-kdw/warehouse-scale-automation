# TASK-0011: Frontend UI/UX Refinement (v2)

**Goal**: Implement strict user controls, better input handling (Scale/Barcode), and data views according to updated specs.

**Assigned to**: Frontend Agent

---

## 1. Draft Entry (All Modes)

### Operator Mode (Single Entry)
- [ ] **Mode Toggle**: Add "Manual / Scale" toggle (SegmentedControl).
  - **Manual**: Number input enabled.
  - **Scale**: Read-only input (placeholder "Waiting for scale...").
- [ ] **Persistence**: Save `draftEntry.quantityMode` to localStorage.
- [ ] **Barcode Listener**:
  - **Logic**: Listen for continuous rapid input (burst < 50ms) + Terminator (Enter/Tab).
  - **Safety**: Do NOT override user if they are explicitly typing in a `textarea` or `input`.
  - **Action**: Auto-fill Article + Select best batch (FEFO).

### Admin Mode (Bulk Entry)
- [ ] **Columns**:
  - **Location**: Read-only "13".
  - **Article**: Auto-fill name/mfr/uom on selection.
  - **Manufacturer**: Auto-fill (read-only).
  - **Batch**: Dropdown filtered by Article.
- [ ] **Actions**:
  - **"Save as Draft"**: Validate only basics.
  - **"Approve Now"**: Strict validation + execute approval.
- [ ] **UX Polish**:
  - Auto-focus article field on "Add Row".
  - "Duplicate Row" button.
  - Keyboard nav (Enter -> next cell).

---

## 2. Receiving (Post to Stock)

- [ ] **Rename**: Update page title to "Post to Stock" / "Unos na stanje".
- [ ] **Form**:
  - Add `Order Number` field (**REQUIRED**).
  - Show validation error if tried to submit without it.
- [ ] **History Tab**:
  - View "Receipts" (grouped by Order Number).
  - Click receipt -> Modal with line items.
  - **Backend Dependency**: `GET /api/inventory/receipts` (Task-0010).

---

## 3. Inventory View

- [ ] **Tabs**: "Paint" vs "Consumables".
- [ ] **Consumables View**:
  - Filter logic: `is_paint === false`.
  - Column `Batch`: Display "—" (Since system batch is internal).
- [ ] **Batch Expiry**:
  - Add Tooltip: "Expires on YYYY-MM-DD (in X days)".
- [ ] **Error Handling**:
  - If API fails, show "Retry" button (not empty state).

---

## 4. Draft Approval View

- [ ] **List**: Show `line_count` and `total_qty` badges.
- [ ] **Actions**: Add "Rename" button for groups (calls `PATCH /api/draft-groups/{id}`).

---

## 5. Verification Steps (Frontend)

- [ ] **Toggle**: Refresh page -> Mode persists.
- [ ] **Barcode**: Focus note -> Scan -> Note text preserved?
- [ ] **Receiving**: Submit empty order number -> Blocked?
- [ ] **Inventory**: Check tabs separate Paint/Consumables correctly.
