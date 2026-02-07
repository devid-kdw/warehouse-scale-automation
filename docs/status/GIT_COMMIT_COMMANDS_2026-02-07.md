# Git Commit Commands - 2026-02-07

# 1. Commit Documentation Changes
git add docs/team/CHANGELOG.md docs/team/PROJECT_KNOWLEDGE.md docs/status/DAILY.md docs/tasks/TASK-0010-backend-refinement.md docs/tasks/TASK-0011-frontend-refinement.md
git commit -m "docs: update project knowledge, changelog, and task briefs for v2 refinement"

# 2. Commit Backend Changes
git add backend/app/models/transaction.py backend/app/models/draft_group.py backend/app/api/draft_groups.py backend/app/api/inventory.py backend/migrations/versions/
git commit -m "backend: add order_number to transaction, atomic approval, and draft naming logic (TASK-0010)"

# 3. Commit Frontend Changes
git add desktop-ui/src/pages/Drafts/ desktop-ui/src/pages/Receiving/ desktop-ui/src/pages/Inventory.tsx desktop-ui/src/api/
git commit -m "ui: implement manual/scale toggle, barcode listener, and inventory tabs (TASK-0011)"

# 4. Status Check
git status
