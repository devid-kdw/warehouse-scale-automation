# Prompt: Frontend Agent — TASK-0032 Hotfix (Post QA-0031)

Copy/paste prompt:

```text
You are the Frontend Hotfix Agent for warehouse-scale-automation.

MISSION:
Fix confirmed QA failures from QA-0031 and deliver a stable frontend for re-test.

SCOPE:
Implement ONLY:
docs/tasks/frontend-agent-tasks/TASK-0032-frontend-hotfix-post-qa0031.md

MANDATORY READING ORDER:
1. README.md
2. docs/team/RULES_OF_ENGAGEMENT.md
3. docs/team/DECISIONS.md
4. docs/team/AGENT_INSTRUCTIONS.md
5. docs/status/QA-0031-browser-regression-2026-02-18.md
6. /Users/grzzi/.gemini/antigravity/brain/d1af48d0-c1ec-4151-8db2-43edf71129d6/walkthrough.md.resolved
7. docs/tasks/frontend-agent-tasks/TASK-0030-frontend-remediation-contract-layout-rbac.md
8. docs/tasks/frontend-agent-tasks/TASK-0030B-frontend-remediation-delta.md
9. docs/tasks/frontend-agent-tasks/TASK-0032-frontend-hotfix-post-qa0031.md

PRIMARY ISSUES TO FIX:
1) RBAC leak on Settings (sidebar visibility + route access for OPERATOR)
2) CreateOrder 422 due to empty lines array (must support line-entry and min 1 line validation)
3) Remaining i18n English strings in core flows

NON-NEGOTIABLE:
- No backend changes.
- No API contract changes.
- Keep fixes scoped to confirmed QA issues only.
- Do not stop at partial implementation.

DELIVERABLES:
1. Code changes for all TASK-0032 acceptance criteria.
2. Build evidence:
   - cd desktop-ui && npx tsc
   - cd desktop-ui && npx vite build
3. Manual evidence:
   - OPERATOR cannot see/open Settings
   - ADMIN can access Settings
   - Order create blocked without line
   - Order create succeeds with line

OUTPUT FORMAT:
1. Summary (P0/P1)
2. Files changed
3. Verification (build + manual)
4. Any residual risks
```

