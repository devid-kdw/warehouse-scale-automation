# Git Commit Commands (2026-02-07 - Final)

Run these commands in your terminal to commit the changes.

## 1. Documentation Updates
```bash
git add docs/team/CHANGELOG.md docs/team/PROJECT_KNOWLEDGE.md docs/status/DAILY.md README.md docs/status/VERIFICATION_REPORT_2026-02-07_FINAL.md docs/tasks/TASK-0014-frontend-final.md docs/tasks/TASK-0015-backend-final.md
git commit -m "docs: update knowledge base and changelog for v2.1 fixes"
```

## 2. Backend Fixes (Consumables Logic)
```bash
git add backend/app/schemas/draft_groups.py backend/app/services/draft_group_service.py backend/tests/test_shortage_draft.py
git commit -m "backend: fix consumables handling in draft groups (allow null batch_id)"
```

## 3. Frontend Fixes (Bulk Entry + Security)
```bash
git add desktop-ui/src/pages/Drafts/BulkDraftEntry.tsx desktop-ui/electron/main.ts
git commit -m "ui: fix bulk entry for consumables and harden electron security"
```

## 4. Final Verification
```bash
# Optional: Tag this release
# git tag -a v1.1.0-beta -m "Core Refinement v2.1"
```
