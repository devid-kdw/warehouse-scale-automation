# Task Brief: TASK-0018 — Backend Contract, RBAC, and Documentation Alignment

**Created**: 2026-02-12  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0-Critical (RBAC consistency), P1-High (API contract bugs), P2-Medium (error semantics/docs)

---

## 🎯 Goal

Align backend behavior with locked project rules and frontend contracts, remove API inconsistencies, and update backend-owned documentation so agents and UI can rely on one coherent source of truth.

---

## 📖 Mandatory Reading Before Coding

1. `docs/team/RULES_OF_ENGAGEMENT.md` (LOCKED rules, especially RBAC + location + transaction policy)
2. `docs/team/DECISIONS.md` (current decisions and policy conflicts)
3. `docs/team/AGENTS.md` (agent boundaries)
4. `docs/tasks/TASK-0010-backend-refinement.md`
5. `docs/tasks/TASK-0016-backend-bugfixes.md`
6. `PROJECT_SPECIFICATION.md`

---

## 📋 Scope

### In Scope
- Fix RBAC leakage on reports endpoints.
- Resolve/implement inventory-visibility RBAC policy on backend after orchestrator decision is logged.
- Fix transaction filtering bug on `/api/transactions`.
- Extend inventory summary contract with `is_paint` required by frontend tabs.
- Enforce case-insensitive alias uniqueness and lookup behavior.
- Improve auth/login error semantics (avoid collapsing credential errors into generic token errors).
- Update backend-owned docs that are now inconsistent with implementation.

### Out of Scope
- New business features unrelated to contract alignment.
- Frontend UI implementation changes (documented in TASK-0019).
- Large refactors that change endpoint shapes beyond described fixes.

---

## 🔴 Blocker / Decision Gate (Must Be Resolved First)

There is a policy conflict across project docs:
- `docs/team/RULES_OF_ENGAGEMENT.md` says OPERATOR can view inventory.
- `docs/team/DECISIONS.md` and `docs/team/AGENTS.md` describe OPERATOR as draft-entry only.

**Required action before code merge**:
1. Orchestrator logs final decision in `docs/team/DECISIONS.md`.
2. Orchestrator syncs conflicting docs (`RULES_OF_ENGAGEMENT.md`, `AGENTS.md`, `PROJECT_KNOWLEDGE.md`).
3. Backend implementation follows that final decision.

If no new decision is logged, treat this task as **blocked**.

---

## 🔧 Technical Changes

### 1) Reports RBAC Must Be ADMIN-Only

**Files**:
- `backend/app/api/reports.py`

**Current issue**:
- Endpoints are JWT-protected but not role-protected.

**Required change**:
- Add `@require_roles('ADMIN')` to:
  - `GET /api/reports/inventory`
  - `GET /api/reports/transactions`
- Add `403` alt responses in docs for both routes.

---

### 2) Inventory View RBAC Consistency (Decision-Driven)

**Files**:
- `backend/app/api/inventory.py`

**Current issue**:
- `/api/inventory/summary` is ADMIN-only, while locked docs are inconsistent.

**Required change**:
- Apply RBAC according to final orchestrator decision (see blocker section).
- If decision = OPERATOR can view inventory:
  - allow `@require_roles('ADMIN', 'OPERATOR')` on summary endpoint.
- If decision = ADMIN-only:
  - keep endpoint ADMIN-only and ensure all docs reflect this.

---

### 3) Transaction Query Filter Bug (`from` vs `from_`)

**Files**:
- `backend/app/api/transactions.py`
- `backend/app/schemas/transactions.py`

**Current issue**:
- Schema uses field `from_` with `data_key='from'`.
- Endpoint checks `if 'from' in args` and reads `args['from']`, so filter is not applied correctly.

**Required change**:
- In endpoint, use `args.get('from_')` and filter with that value.
- Keep public query param as `from` (via `data_key`) unless you intentionally version API.

---

### 4) Inventory Summary Contract: Add `is_paint`

**Files**:
- `backend/app/api/inventory.py`
- `backend/app/schemas/inventory.py`
- tests for inventory summary endpoint

**Current issue**:
- Frontend expects `is_paint` in inventory items for Paint/Consumables tabs.
- Backend summary response omits it.

**Required change**:
- Include `is_paint` in each summary item payload.
- Add schema field and test assertions.

---

### 5) Alias Rules: Case-Insensitive Uniqueness and Lookup

**Files**:
- `backend/app/services/article_alias_service.py`
- potentially migration/model constraints if required
- alias tests

**Current issue**:
- Alias checks are case-sensitive, conflicting with documented case-insensitive behavior.

**Required change**:
- Normalize alias input (trim + canonical case strategy).
- Enforce case-insensitive uniqueness at application level and, if needed, DB level.
- Lookup (`resolve_article`) should be case-insensitive for both alias and article_no query path if policy requires.

---

### 6) Auth Error Semantics (Credential vs Token Errors)

**Files**:
- `backend/app/error_handling.py`
- `backend/app/api/auth_api.py`
- auth tests

**Current issue**:
- Login credential failures can surface as generic token error code semantics.

**Required change**:
- Preserve meaningful auth codes for login failures (e.g., invalid credentials) without breaking existing frontend parsing.
- Update tests to assert intended behavior.

---

### 7) Backend-Owned Documentation Sync

**Files**:
- `backend/README.md`
- `docs/team/CHANGELOG.md`
- optionally `docs/team/DECISIONS.md` if this task introduces finalized policy updates

**Required change**:
- Fix refresh-token lifetime docs to match config (`7 days` unless config changed).
- Remove outdated location statement(s) that still mention `location_id=1` if policy is now `13`.
- Ensure changelog entry is consistent with actual state after this task.

---

## ✅ Acceptance Criteria

1. [ ] Reports endpoints require ADMIN role and return 403 for OPERATOR.
2. [ ] Inventory summary RBAC matches final logged decision and docs are consistent.
3. [ ] `/api/transactions?from=...` correctly filters by lower datetime bound.
4. [ ] Inventory summary includes `is_paint` in every item.
5. [ ] Alias creation and resolution are case-insensitive per policy.
6. [ ] Login/auth errors preserve meaningful credential semantics.
7. [ ] Backend docs are synchronized with implementation (token expiry/location policy).
8. [ ] Relevant pytest coverage added/updated and passing in a valid DB-enabled environment.

---

## 🧪 Test Plan

```bash
# Full backend suite (DB-enabled environment)
pytest backend/tests/ -v

# Focused suites
pytest backend/tests/test_auth.py -v
pytest backend/tests/test_article_aliases.py -v
pytest backend/tests/test_inventory_summary.py -v
pytest backend/tests/test_inventory_receipts.py -v
pytest backend/tests/test_draft_groups.py -v
```

Manual API checks (Swagger or curl):
1. Login as OPERATOR, call `/api/reports/transactions` -> expect 403.
2. Call `/api/transactions?from=<iso>` -> verify lower bound works.
3. Call `/api/inventory/summary` -> each item contains `is_paint`.
4. Create alias with mixed case, attempt duplicate alias in different case -> expect conflict.

---

## 📚 Related

- `docs/tasks/TASK-0010-backend-refinement.md`
- `docs/tasks/TASK-0016-backend-bugfixes.md`
- `docs/tasks/TASK-0019-frontend-contract-rbac-alignment.md`
- `docs/status/ORCHESTRATOR_REVIEW_2026-02-10.md`

---

**Status Updates**:
- 2026-02-12: Task created by Orchestrator from full-project audit findings.
