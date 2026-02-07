# TASK-0015: Backend Final Fixes (Consumables Support)

**Goal**: Enable creation of Draft Groups containing Consumable items without requiring a Client-side Batch ID.

**Assigned to**: Backend Agent

---

## 🚨 P0 - Consumables Schema & Logic
The current `DraftGroupLineSchema` enforces `batch_id` as `required=True`. This forces the Frontend to select a batch even for Consumables (which should use the system "NA" batch).

### 1. Schema Update (`schemas/draft_groups.py`)
- [ ] Update `DraftGroupLineSchema`:
  - Set `batch_id` to `load_default=None` (or `allow_none=True`, `required=False`).
  - Ensure it validates as `Integer` OR `None`.

### 2. Service Logic (`services/draft_group_service.py`)
- [ ] In `create_group`:
  - Iterate through lines.
  - If `line_data.get('batch_id')` is `None`:
    - Fetch the **Article** for that line.
    - If `article.is_paint == True`: Raise `AppError` ("Batch ID required for Paint articles").
    - If `article.is_paint == False` (Consumable):
      - Look up the **System Batch** (Code="NA") for this article.
      - **Logic**: Consumables use a "System Batch" (Code="NA"). You might need to `get_or_create` this batch if it doesn't exist (similar to `receiving_service`).
      - Assign this `batch_id` to the draft.

### 3. Verification
- [ ] **Test**: Create a Draft Group with one Consumable line where `batch_id` is `null`.
- [ ] **Expectation**: Success. Created draft has valid `batch_id` pointing to "NA" batch.
- [ ] **Test**: Create a Draft Group with Paint line where `batch_id` is `null`.
- [ ] **Expectation**: Failure (400/422).

---

## ✅ Deliverable
- Updated Schema.
- Updated Service.
- Passing Test.
