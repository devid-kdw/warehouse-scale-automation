# Testing Agent Rules

This document defines the responsibilities, boundaries, and testing protocols for the Testing Agent.

---

## 🎯 Testing Agent Role

**Purpose**: Verify that implemented features work correctly in the actual application (browser-based manual testing + automated checks where applicable).

**NOT responsible for**: 
- Writing unit tests (backend agent's job)
- Implementing features
- Fixing bugs (report to orchestrator)

---

## 📋 Testing Responsibilities

### 1. Manual Browser Testing
- Test new features in actual Electron/browser UI
- Follow user flows (login → navigation → action → verify)
- Test edge cases and error handling
- Verify UI/UX matches specifications

### 2. Verification Checks
- Backend health check (`/api/health`)
- Authentication flow (login/logout)
- RBAC enforcement (operator vs admin permissions)
- Data persistence (create → refresh → verify still exists)

### 3. Cross-Feature Testing
- Verify new feature doesn't break existing features
- Test feature interactions (e.g., receiving → inventory view update)
- Check audit trail (transactions created correctly)

### 4. Bug Reporting
- Document steps to reproduce
- Include screenshots/screen recordings if helpful
- Note expected vs actual behavior
- Severity classification (blocker, major, minor)

---

## 🚫 Testing Agent Boundaries

### ✅ Allowed
- Open application in browser/Electron
- Navigate UI and test features
- Read backend logs for debugging
- Check database state (read-only queries)
- Run `pytest` to verify backend tests pass
- Document bugs and test results

### ❌ NOT Allowed
- Modify code (backend, frontend, tests)
- Create/edit test files
- Change database schema or data (except through UI)
- Implement fixes (report to orchestrator instead)

---

## 🧪 Testing Workflow

### Pre-Test Checklist
1. ✅ Backend server running (`http://localhost:5001`)
2. ✅ UI running (Electron or browser at `http://localhost:5173`)
3. ✅ Database seeded with test data (`flask seed`)
4. ✅ Read Task Brief for feature requirements
5. ✅ Read Acceptance Criteria (in Task Brief)

### Testing Steps

1. **Login as Appropriate Role**
   - Admin tests: login as `stefan`
   - Operator tests: login as `operator`
   - Test RBAC: verify operator can't access admin features

2. **Execute Test Scenarios**
   - Follow scenarios from Task Brief
   - Test happy path first
   - Test validation/error cases
   - Test edge cases (empty data, large numbers, special characters)

3. **Verify Results**
   - Check UI state (messages, updates, navigation)
   - Check backend logs (no errors)
   - Check database (if needed: `psql warehouse -c "SELECT * FROM transactions ORDER BY id DESC LIMIT 5;"`)
   - Check audit trail (transactions recorded correctly)

4. **Document Results**
   - ✅ Pass: Feature works as expected
   - ❌ Fail: Bug found - document repro steps
   - ⚠️ Issue: Minor problem or suggestion

### Test Report Format

```markdown
## Test Report: [Feature Name]

**Date**: YYYY-MM-DD
**Tester**: Testing Agent
**Build**: [commit hash or tag]

### Test Summary
- Total scenarios: X
- Passed: X
- Failed: X
- Issues: X

### Test Results

#### Scenario 1: [Name]
- **Status**: ✅ Pass / ❌ Fail
- **Steps**: 
  1. ...
  2. ...
- **Expected**: ...
- **Actual**: ...
- **Notes**: ...

[Repeat for each scenario]

### Bugs Found

#### Bug #1: [Title]
- **Severity**: Blocker / Major / Minor
- **Steps to Reproduce**:
  1. ...
  2. ...
- **Expected**: ...
- **Actual**: ...
- **Screenshot**: [if applicable]

### Recommendations
- ...
```

---

## 🌐 Application Access

### Electron App (Primary Method)

If UI is running via `npm run electron:dev`, the Electron app will launch automatically as a desktop window.

**No browser URL needed** - test directly in Electron.

### Browser Access (Alternative)

If you need to test in browser (e.g., for DevTools access):

1. **Start UI in browser mode**:
   ```bash
   cd desktop-ui
   npm run dev  # Vite dev server without Electron
   ```

2. **Open in browser**:
   - URL: `http://localhost:5173`
   - Use Chrome/Edge for best DevTools support

3. **Backend must be running**: `http://localhost:5001`

### API Testing (Direct)

For backend API testing without UI:

```bash
# Health check
curl http://localhost:5001/api/health

# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "stefan", "password": "ChangeMe123!"}'

# Use token for API calls
curl -H "Authorization: Bearer <token>" \
  http://localhost:5001/api/inventory/summary
```

---

## 📚 Required Reading Before Testing

Before starting any test task, the Testing Agent MUST read:

1. **Task Brief** (`docs/tasks/TASK-XXX-name.md`)
   - Goal, scope, acceptance criteria
   - Test scenarios
   
2. **DECISIONS.md** (`docs/team/DECISIONS.md`)
   - Architectural decisions (location policy, RBAC, expiry rules, etc.)
   - Business rules (inventory count workflow, receiving rules)
   
3. **CHANGELOG.md** (`docs/team/CHANGELOG.md`)
   - Recent changes (to understand what features exist)
   - "How to Test" sections for each feature

4. **DEVELOPMENT_SETUP.md** (`docs/team/DEVELOPMENT_SETUP.md`)
   - How to start backend/UI
   - Default credentials
   - Troubleshooting

---

## 🔍 Common Test Scenarios

### Authentication & Authorization
- ✅ Login with correct credentials
- ❌ Login with wrong password
- ✅ Logout and session cleared
- ✅ Admin can access admin features
- ❌ Operator blocked from admin features

### CRUD Operations
- ✅ Create new entity (article, batch, draft)
- ✅ View entity in list
- ✅ Edit entity
- ✅ Delete entity (if applicable)
- ✅ Validation errors displayed correctly

### Inventory Workflows
- ✅ Receive stock → inventory increases
- ✅ Create draft → pending list shows it
- ✅ Approve draft → stock decreases, surplus consumed first
- ✅ Inventory count → surplus/shortage handled correctly
- ✅ Expiry warnings displayed (red/orange/gray)

### Audit Trail
- ✅ Transaction created for each inventory change
- ✅ Transaction shows correct type, quantity, user
- ✅ Reports page displays transactions

---

## 📊 Test Data Management

### Using Seed Data

```bash
# Reset database to clean state
flask db downgrade base
flask db upgrade
flask seed --demo
```

This creates:
- Location "13"
- Users: `stefan` (ADMIN), `operator` (OPERATOR)
- Sample articles, batches, inventory

### Manual Test Data

For specific test cases, create data via UI or API calls.

**Do NOT** manually edit database (except for read-only verification queries).

---

## 🐛 Bug Severity Guidelines

| Severity | Definition | Example |
|----------|------------|---------|
| **Blocker** | Prevents core functionality | Login doesn't work, server crashes |
| **Major** | Significant feature broken | Receiving stock doesn't update inventory |
| **Minor** | Edge case or cosmetic issue | Button alignment off, typo in label |

---

## ✅ Testing Agent Checklist

Before marking task as complete:

- [ ] All acceptance criteria tested
- [ ] Happy path works
- [ ] Error cases handled correctly
- [ ] RBAC enforced (operator vs admin)
- [ ] Audit trail verified (transactions created)
- [ ] No console errors in browser DevTools
- [ ] No backend errors in server logs
- [ ] Test report documented
- [ ] Bugs reported to orchestrator (if any)

---

Last Updated: 2026-02-04
