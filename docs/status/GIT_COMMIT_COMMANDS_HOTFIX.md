# Git Commit Commands (v2.1.1 Hotfix)

Since `task.md` is an internal agent file, we only need to commit the actual project changes (Inventory Hotfix).

```bash
# 1. Add the Inventory Hotfix Changes
git add backend/app/api/inventory.py backend/app/schemas/inventory.py docs/team/CHANGELOG.md

# 2. Add the Commit Command file itself (optional, but good for history)
git add docs/status/GIT_COMMIT_COMMANDS_HOTFIX.md

# 3. Commit
git commit -m "fix(backend): inventory float casting + serialization (v2.1.1)"

# 4. Push to main
git push origin main
```
