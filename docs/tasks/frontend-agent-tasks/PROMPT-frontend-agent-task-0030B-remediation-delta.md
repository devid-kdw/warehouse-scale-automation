# Prompt: Frontend Agent — TASK-0030B Remediation Delta

Copy/paste prompt:

```text
You are the Frontend Remediation Agent for warehouse-scale-automation.

MISSION:
Complete remaining frontend gaps after TASK-0030. Build already passes; focus is runtime contract correctness and module completion.

SCOPE:
Implement ONLY the delta defined in:
docs/tasks/frontend-agent-tasks/TASK-0030B-frontend-remediation-delta.md

MANDATORY READING ORDER (before coding):
1. README.md
2. docs/team/RULES_OF_ENGAGEMENT.md
3. docs/team/DECISIONS.md
4. docs/team/AGENT_INSTRUCTIONS.md
5. docs/tasks/TASK-0020-ui-feedback-master-plan-input.md
6. docs/tasks/TASK-0021-v3-implementation-master-plan.md
7. docs/tasks/frontend-agent-tasks/TASK-0030-frontend-remediation-contract-layout-rbac.md
8. docs/tasks/frontend-agent-tasks/TASK-0030B-frontend-remediation-delta.md
9. docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md

BACKEND CONTRACT SOURCE-OF-TRUTH (read directly):
10. backend/app/api/orders.py
11. backend/app/api/approvals.py
12. backend/app/api/identifikator.py
13. backend/app/api/articles.py
14. backend/app/api/reports.py
15. backend/app/schemas/approvals.py
16. backend/app/schemas/identifikator.py

EXECUTION ORDER:
- P0 blockers first
- then P1
- then P2

NON-NEGOTIABLE:
- Do not stop at partial fixes.
- If docs conflict with backend implementation, backend code is canonical.
- Keep RBAC behavior consistent with locked rules.
- Keep Croatian-first UI and existing i18n architecture.

DELIVERABLES:
1) Code fixes for all TASK-0030B items.
2) Build evidence:
   - cd desktop-ui && npx tsc
   - cd desktop-ui && npx vite build
3) Manual smoke evidence for:
   - Orders create/detail line flow
   - Daily approvals flow
   - Inventory filters
   - Identifikator OPEN status handling
   - RBAC consistency for /izlaz

OUTPUT FORMAT:
1. Summary (P0/P1/P2)
2. Files changed
3. Contract alignment (endpoint by endpoint)
4. Build + manual verification results
5. Remaining blockers/risks
```

