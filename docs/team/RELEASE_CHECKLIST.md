# Release Checklist

Use this checklist before every release to ensure system stability.

---

## Pre-Release Checklist

### 1. Database
- [ ] Backup production database
  ```bash
  pg_dump -Fc warehouse > backup_$(date +%Y%m%d_%H%M%S).dump
  ```
- [ ] Test migrations on dev database first
  ```bash
  flask db upgrade
  ```
- [ ] Verify migration reversibility (if rollback needed)
  ```bash
  flask db downgrade -1
  flask db upgrade
  ```

### 2. Backend Quality Gates
- [ ] All tests pass
  ```bash
  cd backend
  pytest
  ```
- [ ] No linting errors (if configured)
- [ ] Backend starts without errors
  ```bash
  python run.py
  ```
- [ ] Swagger UI loads successfully
  ```
  http://localhost:5001/swagger-ui
  ```

### 3. Frontend Quality Gates
- [ ] Build succeeds
  ```bash
  cd desktop-ui
  npm run build
  ```
- [ ] No TypeScript errors
- [ ] UI starts and loads
  ```bash
  npm run electron:dev
  ```
- [ ] No console errors in browser DevTools

### 4. Environment & Configuration
- [ ] `.env.example` updated (if new variables added)
- [ ] All required environment variables documented
- [ ] Secrets properly configured (JWT_SECRET_KEY, DATABASE_URL)
- [ ] CORS origins configured correctly

### 5. Documentation
- [ ] `CHANGELOG.md` updated with release notes
- [ ] `README.md` accurate (dependencies, setup steps)
- [ ] API documentation current (Swagger reflects reality)
- [ ] Migration notes in `MIGRATIONS.md` (if applicable)

---

## Smoke Test (Manual)

Execute these steps after deployment to verify core functionality:

### 1. Backend Health
```bash
curl http://localhost:5001/health
# Expected: {"status": "healthy", ...}
```

### 2. Database Connectivity
- [ ] Backend logs show successful DB connection
- [ ] No migration warnings/errors

### 3. Seed Data (if fresh install)
```bash
flask seed
# Expected: Creates location "13", user "stefan" (ADMIN), user "operator"
```

### 4. Authentication Flow
- [ ] Open UI at `http://localhost:5173` (dev) or Electron app
- [ ] Login with `stefan` / password
- [ ] JWT token received and stored
- [ ] User menu shows "stefan (ADMIN)"
- [ ] Logout works

### 5. Core Workflows

#### Inventory Summary
- [ ] Navigate to **Inventory** page
- [ ] See list of articles/batches with stock, surplus, total
- [ ] Expiry dates displayed with color coding (red/orange/gray)
- [ ] Search/filter works

#### Receiving Stock (ADMIN only)
- [ ] Navigate to **Receive Stock** page
- [ ] Select article, enter batch code, quantity, expiry
- [ ] Submit successfully
- [ ] Verify stock increased in Inventory view
- [ ] Check transaction recorded

#### Operator Draft Entry
- [ ] Logout, login as `operator`
- [ ] Navigate to **New Draft** page
- [ ] Create weigh-in draft (article, batch, quantity)
- [ ] Submit successfully
- [ ] Verify draft appears in pending list

#### Admin Approval
- [ ] Logout, login as `stefan` (ADMIN)
- [ ] Navigate to **Draft Approval** page
- [ ] See pending draft from operator
- [ ] Approve draft
- [ ] Verify stock/surplus updated correctly
- [ ] Check transaction recorded (WEIGH_IN, SURPLUS_CONSUMED, STOCK_CONSUMED)

#### Inventory Count
- [ ] Navigate to **Inventory** page
- [ ] Click "Count" on an item
- [ ] Enter counted quantity (different from system total)
- [ ] Submit count
- [ ] Verify surplus adjusted OR shortage draft created

#### Reports/Transactions
- [ ] Navigate to **Reports** page
- [ ] See list of recent transactions
- [ ] Filter by date/type works
- [ ] Transaction details visible (type, article, batch, qty, user, timestamp)

---

## Post-Release Verification

### Monitor for 24 Hours
- [ ] Check backend logs for errors
- [ ] Monitor database performance
- [ ] Verify no failed transactions
- [ ] Test on actual warehouse operations (if possible)

### Rollback Plan (if needed)
1. Stop backend/frontend
2. Restore database from backup
   ```bash
   pg_restore -d warehouse backup_YYYYMMDD_HHMMSS.dump
   ```
3. Revert to previous code version (git tag)
4. Restart services

---

## Version Bump

After successful release:
1. Update version in `backend/app/__init__.py` (or `pyproject.toml`)
2. Update version in `desktop-ui/package.json`
3. Tag release in git:
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0 - Added receiving workflow"
   git push origin v1.2.0
   ```
4. Update `CHANGELOG.md` - move [Unreleased] items to new version section

---

**Last Updated**: 2026-02-03
