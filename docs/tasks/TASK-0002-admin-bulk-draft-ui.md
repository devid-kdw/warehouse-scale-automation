# TASK-0002: Admin Bulk Draft UI

**Created**: 2026-02-04  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P1-High  

---

## 🎯 Goal

Enable admins to enter multiple weigh-in drafts simultaneously as a "Draft Group" and approve or reject them atomically.

---

## 📋 Scope

### In Scope
- **Draft Entry screen**:
  - Live under existing `/draft-entry` route with role-based tabs (not a separate route).
  - Multi-line table entry (Article, Batch, Quantity, Note).
  - Article selector: Search by `article_no`, `aliases`, `description`. Display `article_no - description`.
  - Batch selector: Must reset when article changes and handle empty batch states explicitly.
  - Quantity input: Decimal, min > 0, step 0.01. Invalid state blocks submit.
  - Fixed location (ID=1, code="13").
  - "Save as Draft" (POST /api/draft-groups).
  - "Approve Now": Implemented as 2-step sequence (create group -> approve group). If approval fails, group remains in DRAFT.
- **Approval screen**:
  - Group-level list (name, source, count, total qty).
  - Badge for source: "Admin Draft" vs "Auto Draft" with distinct colors.
  - Detail view for groups: Disable Approve/Reject/Rename if status is not DRAFT.
  - Explicit 409 handling: Show user-readable inventory conflict messages.
- **No optimistic updates**: All mutations must invalidate queries and refetch authoritative state.
- **Error handling**: Mantine notifications for API errors (401/403/409/500).

### Out of Scope
- Modifying backend code (assumes TASK-0001 endpoints available).
- Location selection.
- Mobile/Responsive overhaul (standard desktop-first for now).

---

## 🔧 Technical Changes

### Frontend Changes

#### New Pages/Components
- `BulkDraftEntry.tsx` - Table-style entry for multiple drafts.
- `DraftGroupDetail.tsx` - Modal or drill-down view for group lines.

#### Modified Pages
- `DraftEntry.tsx` - Add link/toggle to "Bulk Mode" for admins.
- `Approvals.tsx` - Change list from individual drafts to grouped drafts.

#### API Client (`src/api/services.ts`)
- Add `getDraftGroups()`, `getDraftGroup(id)`, `createDraftGroup()`, `renameDraftGroup()`, `approveDraftGroup()`, `rejectDraftGroup()`.
- Update `types.ts` with labels: `DraftGroup`, `DraftGroupSummary`.

---

## ✅ Acceptance Criteria

1. [ ] Admin can switch to "Bulk Entry" on the Draft Entry page.
2. [ ] Admin can add/remove rows in the bulk entry table.
3. [ ] Admin can save a bulk entry as a "Draft Group".
4. [ ] Approval list shows Groups instead of individual lines.
5. [ ] Clicking a group shows its lines and allows group-level approval/rejection.
6. [ ] Admin can rename a draft group in the approval detail view.
7. [ ] Operators CANNOT see or access bulk entry tools.
8. [ ] Build passes and no console errors occur during use.

---

## 🧪 Test Plan

### Manual Testing
1. **Bulk Creation**:
   - Login as Admin.
   - Go to Draft Entry -> Bulk Entry.
   - Enter 3 items.
   - Click "Save as Draft".
   - Verify success notification.
2. **Approval**:
   - Go to Approvals.
   - Verify the new group appears with "unnamed" or default name.
   - Verify line count = 3.
   - Click to open.
   - Approve the group.
   - Verify stock increases for ALL items.
3. **RBAC**:
   - Login as Operator.
   - Verify "Bulk Entry" is absent.

---

## 📚 Related Documentation
- [TASK-0001-draft-groups.md](./TASK-0001-draft-groups.md)
- [DECISIONS.md - RBAC](../team/DECISIONS.md#role-based-access-control-rbac)
- [RULES_OF_ENGAGEMENT.md](../team/RULES_OF_ENGAGEMENT.md)
