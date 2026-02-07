# TASK-0013: Frontend Stabilization (P0/P1)

**Goal**: Expose Bulk Entry, enforce guards, and clean up usage of legacy settings. "Bulk Entry is available."

**Assigned to**: Frontend Agent

---

## 🚨 P0 - Critical Blockers

### 1. Expose Bulk Draft Entry
- [ ] **Route**: Add route `/drafts/bulk` in `App.tsx`, mapping to `<BulkDraftEntry />`.
- [ ] **Sidebar**: Add "Bulk Entry" link.
- [ ] **Guard**:
  - Requires Authentication.
  - **Admin Only**: If user is Operator, link is hidden or route redirects to `/drafts`.

### 2. Cleanup Legacy Code
- [ ] **Remove**: `useAppSettings` hook (if unused).
- [ ] **Remove**: Calls/imports to `useAppSettings`.
- [ ] **Clean**: Check `STORAGE_KEYS` for obsolete entries.
- [ ] **Build Check**: Ensure implementation builds without new warnings.

---

## 🔒 P1 - Tests (Minimal)

- [ ] **Tests (Optional)**: If time permits, add basic unit test for the Route Guard logic.

---

## ✅ Verification Steps (Frontend)

1.  **Login as Admin**:
    - Sidebar shows "Bulk Entry".
    - Click -> Navigates successfully to `/drafts/bulk`.
2.  **Login as Operator**:
    - Sidebar does **NOT** show "Bulk Entry".
    - Direct navigation to `/drafts/bulk` redirects or shows Forbidden.
3.  **Code Check**: No `useAppSettings` imports remain.
