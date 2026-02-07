# TASK-0014: Frontend Final Fixes (Bulk Entry & Security)

**Goal**: Fix Bulk Entry UI for consumables and harden Electron security.

**Assigned to**: Frontend Agent

---

## 🚨 P0 - Bulk Entry Consumables Check

### 1. Update `BulkDraftEntry.tsx`
- [ ] **Row Component**:
  - Check `selectedArticle?.is_paint`.
  - **If `false` (Consumable)**:
    - **Hide** the "Batch" Select dropdown.
    - **Show** a Badge or Text: "System Batch (NA)" (Visual feedback).
    - **Logic**: When adding/updating this row, set `batch_id` to `null` (or don't send it).
  - **If `true` (Paint)**:
    - Keep current behavior (Batch Select required).
- [ ] **Verification**:
  - Select "Sandpaper" (Consumable) -> Batch dropdown disappears -> "System Batch" appears.
  - Select "Red Paint" (Paint) -> Batch dropdown appears.

---

## 🔒 P1 - Electron Security Hardening

### 2. Update `electron/main.ts`
- [ ] **Disable Node Integration**:
  - `webPreferences.nodeIntegration: false`.
  - `webPreferences.contextIsolation: true` (Keep/Verify).
- [ ] **Verify App**:
  - Launch app.
  - Log in.
  - Check if any functionality breaks (e.g. printing, generic fs access).
  - *Note*: If the app relies on `ipcRenderer`, ensure it is exposed via `preload.js`. If `nodeIntegration: false` breaks the app critically, **document why** and revert, but try to fix first.
  
---

## ✅ Deliverable
- Updated `BulkDraftEntry.tsx` handling Consumables.
- Updated `electron/main.ts` with security flags.
