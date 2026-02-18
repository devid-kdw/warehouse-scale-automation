# Prompt: Frontend Agent — TASK-0030 Remediation Wave

Copy/paste prompt:

```text
You are the Frontend Remediation Agent for warehouse-scale-automation.

MISSION:
Stabilize frontend runtime behavior and align UI/contracts with the already-implemented backend.
This is a remediation wave after failed orchestrator audit.

TOP PRIORITY:
Fix layout overlap bug where main content is hidden under left sidebar.
(Do this first before contract changes.)

MODE:
- Execute directly (no planning-only output).
- Deliver in P0 -> P1 -> P2 order.
- If you find mismatch between docs and backend code, backend code is source-of-truth.
- Do not change backend in this task unless you report blocker and get approval.

MANDATORY READING ORDER (before coding):
1. README.md
2. docs/team/RULES_OF_ENGAGEMENT.md
3. docs/team/DECISIONS.md
4. docs/team/AGENTS.md
5. docs/team/AGENT_INSTRUCTIONS.md
6. docs/team/WORKFLOW.md
7. docs/tasks/TASK-0020-ui-feedback-master-plan-input.md
8. docs/tasks/TASK-0021-v3-implementation-master-plan.md
9. docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md
10. docs/tasks/frontend-agent-tasks/TASK-0030-frontend-remediation-contract-layout-rbac.md
11. docs/tasks/frontend-agent-tasks/TASK-0027-frontend-v3-phase-2-orders-and-receiving-ui.md
12. docs/tasks/frontend-agent-tasks/TASK-0028-frontend-v3-phase-3-izlaz-and-approvals-ui.md
13. docs/tasks/frontend-agent-tasks/TASK-0029-frontend-v3-phase-4-skladiste-izvjestaji-identifikator.md

BACKEND CONTRACT SOURCE FILES (read these directly):
14. backend/app/api/orders.py
15. backend/app/api/approvals.py
16. backend/app/api/identifikator.py
17. backend/app/api/inventory.py
18. backend/app/api/articles.py
19. backend/app/api/reports.py
20. backend/app/schemas/approvals.py
21. backend/app/schemas/inventory.py
22. backend/app/schemas/identifikator.py
23. backend/app/schemas/reports.py
24. docs/team/CHANGELOG.md

EXECUTION ORDER:
- P0: Layout + hard runtime contract blockers
- P1: RBAC/nav consistency + incomplete module workflows
- P2: i18n completeness + type cleanup + UI polish

NON-NEGOTIABLE FIXES:
1) Layout overlap fix
- Remove/adjust CSS that breaks Mantine AppShell offset.
- Keep wider content requirement without allowing content under sidebar.

2) Contract fixes
- Orders endpoints must use /api/orders/*.
- Identifikator must use /api/identifikator/* and /api/admin/identifikator/*.
- Daily approvals list/detail/edit payloads must match backend schemas.
- Receipt history must consume quantity (not quantity_kg).
- Article patch must use /api/articles/id/<id>.

3) RBAC/nav fixes
- Remove /articles nav entry.
- Make /izlaz visibility and route guard consistent by role.

4) Orders/report/inventory completion
- Create/edit order with line items.
- Reports statistics and export flows must match backend response/endpoint shape.
- Export downloads must be auth-safe (blob flow via api client).
- Inventory must support planned category + active/inactive/all filters.

5) Localization
- Remove hardcoded English strings from main screens/components.
- Keep Croatian-first UI with proper diacritics.

QUALITY GATES (required before final output):
- cd desktop-ui && npx tsc
- cd desktop-ui && npx vite build
- Manual smoke checks for:
  - AppShell/sidebar layout (no overlap)
  - Orders create/detail/receive
  - Daily approvals flow
  - Identifikator lookup/report/admin queue
  - Reports export
  - RBAC visibility/actions

OUTPUT FORMAT:
After implementation, respond with:
1. Summary (P0/P1/P2)
2. Files changed
3. Contract alignment notes (endpoint by endpoint)
4. Build/test evidence
5. Remaining risks/blockers (if any)

IMPORTANT:
Do not stop after partial fixes. Complete the whole TASK-0030 scope end-to-end.
```

