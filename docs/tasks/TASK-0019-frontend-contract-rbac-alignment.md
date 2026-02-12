# Task Brief: TASK-0019 — Frontend Contract, RBAC, and UX Alignment

**Created**: 2026-02-12  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0-Critical (RBAC consistency), P1-High (contract mismatches), P2-Medium (docs cleanup)

---

## 🎯 Goal

Align frontend behavior with backend API contracts and locked project rules, remove endpoint/query mismatches, and ensure key screens (Inventory, Approvals, Reports) behave consistently in production.

---

## 📖 Mandatory Reading Before Coding

1. `docs/team/RULES_OF_ENGAGEMENT.md` (LOCKED rules, especially RBAC)
2. `docs/team/DECISIONS.md` (active policy decisions and known conflicts)
3. `docs/team/AGENTS.md` (frontend boundaries)
4. `docs/tasks/TASK-0011-frontend-refinement.md`
5. `docs/tasks/TASK-0017-frontend-cleanup.md`
6. `docs/tasks/TASK-0018-backend-contract-rbac-alignment.md` (backend dependency contract)

---

## 📋 Scope

### In Scope
- Fix Reports page request/contract mismatches.
- Fix Draft Group detail data mapping mismatch (`lines` vs `drafts`).
- Align Inventory tab filtering with actual backend contract (including `is_paint` once backend ships fix).
- Apply route/sidebar RBAC behavior according to final orchestrator decision for operator inventory access.
- Update frontend-owned README/docs text that no longer reflects JWT-based flow.

### Out of Scope
- New major UI modules.
- Backend endpoint implementation (handled in TASK-0018).
- Design system redesign.

---

## 🔴 Blocker / Decision Gate (Must Be Resolved First)

Same RBAC policy conflict as backend task:
- `RULES_OF_ENGAGEMENT.md` says OPERATOR can view inventory.
- Other docs currently describe OPERATOR as draft-only.

**Required action before code merge**:
1. Orchestrator logs final decision in `docs/team/DECISIONS.md`.
2. Frontend route/sidebar behavior follows that final decision.

If no decision exists, treat RBAC route change as blocked.

---

## 🔧 Technical Changes

### 1) Reports Page Must Match Backend Query Contract

**Files**:
- `desktop-ui/src/pages/Reports.tsx`
- `desktop-ui/src/api/services.ts`
- optionally `desktop-ui/src/api/types.ts`

**Current issue**:
- Page sends params (`page`, `search`, `type`, `start_date`, `end_date`) that backend `/api/transactions` does not consume.
- Type filter values (`CONSUMPTION`, `ADJUSTMENT`) do not match backend enum.

**Required change**:
- Send backend-supported params: `tx_type`, `from`, `to`, `limit`, `offset`, and supported IDs if used.
- Replace type options with backend-supported transaction types.
- Keep UI behavior predictable when filters are empty.

---

### 2) Draft Group Detail Data Mapping Fix

**Files**:
- `desktop-ui/src/pages/Approvals/DraftGroupDetail.tsx`
- `desktop-ui/src/api/types.ts`

**Current issue**:
- Component renders `group.lines`, but backend schema returns nested `drafts`.

**Required change**:
- Align with backend contract:
  - either map API response to `lines` in service layer, or
  - update component/types to consume `drafts` directly.
- Ensure line table renders reliably.

---

### 3) Inventory Tabs Contract Alignment (`is_paint`)

**Files**:
- `desktop-ui/src/pages/Inventory.tsx`
- `desktop-ui/src/api/types.ts`

**Current issue**:
- Frontend filters by `item.is_paint`, but backend summary currently may omit it.

**Required change**:
- Coordinate with TASK-0018 backend update that adds `is_paint`.
- Make UI resilient during rollout (safe fallback if missing).
- Ensure consumables display policy remains correct:
  - show consumables separately
  - keep system batch display behavior consistent with task specs.

---

### 4) RBAC Route/Sidebar Alignment (Decision-Driven)

**Files**:
- `desktop-ui/src/App.tsx`
- `desktop-ui/src/components/Sidebar.tsx`

**Current issue**:
- Inventory route currently admin-only.
- Policy is inconsistent across docs.

**Required change**:
- Apply route guards and sidebar visibility based on final orchestrator decision.
- If operators should view inventory:
  - expose read-only inventory route and menu item.
  - keep mutate actions admin-only.
- If admin-only:
  - keep current route protection and ensure docs match.

---

### 5) Frontend Documentation Cleanup

**Files**:
- `desktop-ui/README.md`
- optionally `docs/team/CHANGELOG.md` for summary

**Current issue**:
- README still references obsolete API token / actor ID configuration flow that does not match current JWT login UX.

**Required change**:
- Update setup/config section to actual JWT login workflow and current settings behavior.
- Remove outdated instructions.

---

## ✅ Acceptance Criteria

1. [ ] Reports page sends only backend-supported query params and renders filtered results correctly.
2. [ ] Draft Group detail reliably displays lines from API response.
3. [ ] Inventory tabs (Paint/Consumables) behave correctly with backend `is_paint`.
4. [ ] Route + sidebar RBAC for Inventory matches final logged decision.
5. [ ] `desktop-ui/README.md` reflects current auth/config flow (no obsolete API token/actor ID steps).
6. [ ] `npm run build` passes (TypeScript + Vite compile).

---

## 🧪 Test Plan

```bash
cd desktop-ui
npm run build
```

Manual checks:
1. Reports: apply tx type + date filters, verify backend data changes accordingly.
2. Draft approvals: open group detail modal, verify all lines render.
3. Inventory tabs: verify paint and consumables separation.
4. RBAC:
   - OPERATOR login: verify allowed routes per final decision.
   - ADMIN login: verify full access remains.
5. Settings/login flow: verify README instructions match real app behavior.

---

## 📚 Related

- `docs/tasks/TASK-0011-frontend-refinement.md`
- `docs/tasks/TASK-0017-frontend-cleanup.md`
- `docs/tasks/TASK-0018-backend-contract-rbac-alignment.md`
- `docs/status/ORCHESTRATOR_REVIEW_2026-02-10.md`

---

**Status Updates**:
- 2026-02-12: Task created by Orchestrator from full-project audit findings.
