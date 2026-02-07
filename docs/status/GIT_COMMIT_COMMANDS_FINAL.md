# Git Commit Komande - 2026-02-04 (FINAL)

Sve promjene su pregledane. Preporučujem **2 odvojena commita** za jasnoću povijesti.

---

## 1. Commit: Agent Dokumentacija

Ovaj commit sadrži samo nove dokumente za orkestraciju i agente.

```bash
# 1. Prijeđi u folder
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation"

# 2. Stage dokumentaciju
git add README.md
git add docs/team/AGENT_INSTRUCTIONS.md
git add docs/team/DEVELOPMENT_SETUP.md
git add docs/team/QUICK_AGENT_BRIEFINGS.md
git add docs/team/TESTING_AGENT_RULES.md
git add docs/team/CHANGELOG.md
git add docs/status/DAILY.md

# 3. Commit
git commit -m "docs: establish agent coordination infrastructure

- Add DEVELOPMENT_SETUP.md with troubleshooting guide
- Add TESTING_AGENT_RULES.md with protocols
- Add AGENT_INSTRUCTIONS.md for all roles
- Add QUICK_AGENT_BRIEFINGS.md for task assignments
- Update README.md with new doc links"
```

---

## 2. Commit: Feature Updates (Articles & Auth)

Ovaj commit sadrži kodne promjene (Article v1.2 i Auth config).

```bash
# 1. Stage sve ostalo (backend + frontend code)
git add backend/.env.example
git add backend/app/api/articles.py
git add backend/app/api/inventory.py
git add backend/app/api/transactions.py
git add backend/app/config.py
git add backend/app/models/article.py
git add backend/app/schemas/articles.py
git add desktop-ui/src/
git add docs/team/DECISIONS.md

# 2. Commit
git commit -m "feat: upgrade Article model to v1.2 and update Auth config

Backend:
- Article: Add 'uom' (KG/L), 'manufacturer', 'reorder_threshold'
- Deprecate 'base_uom' in favor of strict 'uom'
- Update ArticleSchema validation
- Config: set JWT_REFRESH_EXPIRES_DAYS=7, ACCESS=15min

Frontend:
- Add useAuth hook
- Update API types and endpoints
- Update DraftEntry and Inventory pages

Docs:
- Update DECISIONS.md with Article v1.2 and JWT policies"
```

---

## 3. Push na GitHub

```bash
git push origin main
```

---

## ✅ Verifikacija

Nakon ovoga `git status` bi trebao biti čist (osim ovog file-a s komandama).
