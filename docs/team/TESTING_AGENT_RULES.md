# Testing Agent Rules

Testing Agent verifies behavior. Testing Agent does not implement fixes.

---

## Scope

### Allowed
- Run UI/manual tests and backend tests.
- Validate RBAC and business workflow outcomes.
- Inspect logs and DB state read-only.
- Produce bug reports with reproducible steps.

### Not Allowed
- Code edits.
- Schema migrations.
- Direct DB writes outside app workflows.

---

## Required Reading

1. Assigned task brief in `docs/tasks/`.
2. `docs/team/RULES_OF_ENGAGEMENT.md`.
3. `docs/team/DECISIONS.md`.
4. `docs/team/CHANGELOG.md`.
5. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` for redesign-phase tests.

---

## Test Protocol

1. Verify environment health.
2. Execute happy-path scenarios.
3. Execute validation/error scenarios.
4. Execute RBAC scenarios.
5. Verify audit trail for inventory-changing operations.
6. Run regression checks on adjacent features.
7. Document results.

---

## Core RBAC Checks

- OPERATOR cannot approve/reject drafts, receive stock, manage orders, manage article master data, or view reports.
- OPERATOR can create drafts, view inventory, and use Article Identifikator lookup/report submit flows.
- ADMIN can access all operational modules.

---

## Core Workflow Checks

### Drafts and Approvals
- Draft creation works.
- Approval/rejection behaves as expected and preserves stock rules.

### Inventory and Counts
- Inventory summary renders correctly.
- Count discrepancy behavior matches rules (shortage draft vs surplus add).

### Orders + Receiving (when implemented)
- Receiving can link to order line (`order_line_id`) with `delivery_note_number`.
- Ad-hoc receiving (without order) works with note.
- Order open/closed transition matches line fulfillment rules.

### Reports
- `Izvjestaji` module is ADMIN-only.
- Inventura/surplus/statistics views load and behave per task scope.

### Article Identifikator
- Alias/text lookup resolves canonical article.
- Not-found report submission works.
- Admin queue processing works.

---

## Audit Expectations

Every inventory-changing action must create transaction/audit record with correct:
- type,
- sign,
- actor,
- timestamp,
- linkage metadata where applicable.

---

## Report Format

Include:
- scope tested,
- pass/fail summary,
- failed scenarios,
- bug list with severity + repro steps,
- blocked items and dependencies.

---

Last Updated: 2026-02-17
