# Warehouse Scale Automation

Internal warehouse operations system with controlled inventory flows, approval workflows, and audit trail.

## Current Documentation Authority

When documentation conflicts, use this order:
1. `docs/team/RULES_OF_ENGAGEMENT.md`
2. `docs/team/DECISIONS.md`
3. active planning brief: `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
4. historical task/status documents

## Project Structure

```text
warehouse-scale-automation/
├── backend/
├── desktop-ui/
├── docs/
│   ├── team/
│   ├── tasks/
│   └── status/
├── PROJECT_SPECIFICATION.md
└── README.md
```

## Important Notes

- The product direction is currently in a redesign/planning alignment phase (TASK-0020).
- Many old docs describe earlier implemented states and are kept for traceability.
- Use `docs/team/CHANGELOG.md` for latest documentation and policy updates.

## Quick Start

Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
flask db upgrade
flask seed
python3 run.py
```

Desktop UI:
```bash
cd desktop-ui
npm install
npm run electron:dev
```

## Key Links

- `PROJECT_SPECIFICATION.md`
- `docs/team/DEVELOPMENT_SETUP.md`
- `docs/team/RULES_OF_ENGAGEMENT.md`
- `docs/team/DECISIONS.md`
- `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
- `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
- `docs/tasks/backend-agent-tasks/`
- `docs/tasks/frontend-agent-tasks/`
- `docs/team/CHANGELOG.md`
