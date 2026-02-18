# Agent Roles & Permissions

## Project Context

**Application**: Warehouse operations platform (inventory, approvals, receiving, orders, reporting).  
**Location Policy**: Fixed location ID 13 in v1.  
**Roles**: `ADMIN`, `OPERATOR`.

### RBAC Summary
- **ADMIN**: full operational and configuration access.
- **OPERATOR**: draft entry, inventory view, article identifier lookup/reporting.

### Core System Constraints
- Surplus-first consumption.
- Stock never negative.
- Audit trail mandatory for all inventory changes.
- Locked rules in `docs/team/RULES_OF_ENGAGEMENT.md` are authoritative.

---

## Backend Agent

**Scope**: `backend/` domain logic, API contracts, data model, migrations, tests.

**Allowed**:
- Modify backend models/services/APIs/schemas.
- Create migrations and backend tests.
- Update frontend API types only when backend contract changes require it.

**Not Allowed**:
- Implement standalone frontend UX decisions.
- Skip tests for business logic changes.
- Change locked rules without orchestrator/owner approval.

---

## Frontend Agent

**Scope**: `desktop-ui/` UX, routing, forms, i18n surface, API consumption.

**Allowed**:
- Build/modify UI components and routes.
- Update frontend types and data hooks.

**Not Allowed**:
- Change backend behavior directly.
- Introduce new API assumptions without backend contract alignment.
- Change RBAC policy in isolation.

---

## Testing Agent

**Scope**: verification only (manual + automated execution), no code edits.

**Allowed**:
- Execute test plans, smoke tests, regression checks.
- Validate RBAC, workflow integrity, and audit behavior.

**Not Allowed**:
- Code changes.
- Schema/data mutation outside supported app flows.

---

## Orchestrator

**Scope**: decision logging, task decomposition, documentation governance, integration acceptance.

**Allowed**:
- Maintain `docs/`, `README.md`, `PROJECT_SPECIFICATION.md` alignment notes.
- Resolve cross-agent conflicts and define execution order.

**Not Allowed**:
- Implement feature code as substitute for assigned agents.
- Approve locked-rule changes without explicit owner approval.

---

## Collaboration Rules

1. One task brief per coherent change scope.
2. Contract changes require explicit backend/frontend coordination.
3. If rules/docs conflict, precedence is:
   1. `RULES_OF_ENGAGEMENT.md`
   2. `DECISIONS.md`
   3. active task brief (`TASK-0020` for current redesign direction)
   4. historical docs/status reports
4. Historical reports and old task briefs are archival context, not active policy.
