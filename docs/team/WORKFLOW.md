# Development Workflow

This document defines the standard process for implementing features, fixing bugs, and maintaining the warehouse-scale-automation project.

---

## 🎯 Standard Feature Implementation Flow

### Phase 1: Task Brief (Orchestrator)

**Orchestrator** creates a Task Brief document with:

1. **Goal**: What are we building? (1-2 sentences)
2. **Scope**: What's in scope / out of scope?
3. **Acceptance Criteria**: How do we know it's done?
4. **Test Plan**: How will we verify it works?
5. **Agent Assignment**: Backend Agent, Frontend Agent, or both?

**Output**: `docs/tasks/TASK-NNNN-brief.md` (numbered sequentially)

**Example**:
```markdown
# TASK-0001: Implement Receiving Workflow

## Goal
Add ability to receive new paint batches and increase stock.

## Scope
IN: API endpoint, service logic, transaction logging, basic UI form
OUT: Barcode scanning, mobile app, multi-location

## Acceptance Criteria
- [ ] Admin can enter new batch with expiry date
- [ ] Stock increases correctly
- [ ] Transaction log shows RECEIPT entry
- [ ] UI validates batch code format

## Test Plan
- pytest: test_receiving_service.py
- E2E: Create batch → verify stock increase → check transaction log
```

---

### Phase 2: Backend Implementation (Backend Agent)

**If task requires backend changes:**

1. **Create/modify models** (if new entities needed)
2. **Write migration** (`flask db migrate -m "description"`)
3. **Implement service layer** (business logic in `app/services/`)
4. **Create API endpoint** (in `app/api/`)
5. **Write tests** (`tests/test_*.py`)
6. **Update Swagger docs** (via marshmallow schemas + docstrings)
7. **Update README** (if new environment variables or setup steps)

**Quality Gates**:
- ✅ `pytest` passes (all tests green)
- ✅ Migration works from scratch (`flask db downgrade base && flask db upgrade head`)
- ✅ Swagger UI accessible at `/api/docs/` and documents new endpoint
- ✅ No breaking changes to existing API payloads (unless versioned)

**Output**: 
- PR with backend changes
- Update `docs/team/PROJECT_DASHBOARD.md` with progress

---

### Phase 3: Frontend Implementation (Frontend Agent)

**If task requires UI:**

1. **Create/modify components** (`desktop-ui/src/components/`)
2. **Add pages/routes** (if new screen needed)
3. **Implement API client calls** (`desktop-ui/src/api/`)
4. **Add form validation** (using Mantine + React Hook Form)
5. **Update role-based routing** (if ADMIN/OPERATOR access differs)
6. **Write E2E tests** (basic flow verification)

**Quality Gates**:
- ✅ `npm run build` succeeds (no TypeScript errors)
- ✅ Basic flows work: login → create draft → approve (manual test)
- ✅ No console errors in browser dev tools
- ✅ UI matches role permissions (OPERATOR can't see admin features)

**Output**:
- PR with frontend changes
- Update `docs/team/PROJECT_DASHBOARD.md` with UI screenshots (optional)

---

### Phase 4: Integration & Documentation (Orchestrator)

**Orchestrator** verifies:

1. **Backend + Frontend work together** (E2E flow)
2. **Documentation updated**:
   - `README.md` (if setup changed)
   - `PROJECT_SPECIFICATION.md` (if business rules changed)
   - `docs/team/PROJECT_DASHBOARD.md` (status, what's next)
3. **Task Brief marked complete** (checklist items)

**Output**:
- Merge PRs
- Update dashboard
- Close task

---

## 🐛 Bug Fix Workflow

### Simple Bug (Single Agent)

1. **Identify root cause** (Backend or Frontend)
2. **Assign to appropriate agent**
3. **Fix + add regression test**
4. **Update dashboard** with "Bug fixed: [description]"

### Complex Bug (Cross-Cutting)

1. **Orchestrator investigates** and creates bug report
2. **Assigns to both agents** if affects backend + frontend
3. **Coordinate fix** (backend first, then frontend if needed)
4. **Add integration test** to prevent regression

---

## 🔄 Standard Git Workflow

### Commit Messages

Format: `<type>: <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code restructuring (no behavior change)
- `chore`: Maintenance (dependencies, config)

**Examples**:
- ✅ `feat: add receiving endpoint for new batches`
- ✅ `fix: prevent negative stock in approval service`
- ✅ `docs: update PROJECT_DASHBOARD with v1 status`
- ❌ `updated stuff` (too vague)
- ❌ `WIP` (don't commit WIP to main branch)

### Branch Strategy

- **main**: Production-ready code
- **feature/task-NNNN-description**: Feature branches (delete after merge)
- **bugfix/issue-description**: Bug fixes

### Pull Request Process

1. **Create PR** with clear title and description
2. **Reference Task Brief** (e.g., "Implements TASK-0001")
3. **Self-review checklist**:
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No breaking changes (or clearly documented)
   - [ ] Quality gates met
4. **Request review** from Orchestrator or other agent
5. **Address feedback** and merge

---

## 📋 Quality Standards

### Backend Standards

| Check | Requirement |
|-------|-------------|
| Tests | All new endpoints have pytest tests |
| Migrations | Reproducible from scratch (`db downgrade base && db upgrade head`) |
| Swagger | All endpoints documented in Swagger UI |
| Type Hints | New functions have type hints |
| Error Handling | Use `AppError` for business logic errors |
| Logging | Log important actions (approval, rejection, stock changes) |

### Frontend Standards

| Check | Requirement |
|-------|-------------|
| Build | `npm run build` succeeds with no errors |
| TypeScript | Strict mode enabled, no `any` types |
| Forms | Validation before API calls |
| Error Display | User-friendly error messages (not raw API errors) |
| Role Check | Admin-only features hidden from OPERATOR |
| Basic Flows | Login, create draft, approve draft work |

### Documentation Standards

| Document | Update Trigger |
|----------|----------------|
| `README.md` | New setup steps, environment variables |
| `PROJECT_SPECIFICATION.md` | Business rule changes |
| `docs/team/PROJECT_DASHBOARD.md` | Every completed task/feature |
| Task Brief | When task is completed |

---

## 🚨 When to Pause and Escalate

**STOP and notify Orchestrator if**:

- Breaking change required (API payload modification)
- New database migration conflicts with existing data
- Security concern discovered (auth bypass, injection risk)
- Rule in `RULES_OF_ENGAGEMENT.md` seems incorrect
- Cross-cutting change affects multiple agent domains
- Unexpected complexity (estimate doubles)

**Don't proceed blindly** - escalate and get decision.

---

## 🎉 Definition of Done

A task is **DONE** when:

- ✅ Acceptance criteria met (from Task Brief)
- ✅ Tests pass (backend: pytest, frontend: build + manual flow)
- ✅ Documentation updated
- ✅ Code reviewed and merged
- ✅ `PROJECT_DASHBOARD.md` updated
- ✅ No breaking changes (or properly versioned/documented)

---

## 📊 Progress Tracking

**Orchestrator maintains**:
- Task queue in `docs/team/PROJECT_DASHBOARD.md`
- Current status (In Progress, Blocked, Done)
- Risk/Issue log

**Agents update**:
- Task Brief checklists (mark items done)
- Dashboard "What's Done" section after merge

---

## 🛠️ Daily Standup (Async)

Each agent posts update in dashboard:

1. **What I did**: Completed tasks
2. **What I'm doing**: Current task
3. **Blockers**: Waiting on X, need decision on Y

**Example**:
```markdown
## Frontend Agent Update (2026-02-03)
- ✅ Completed: Receiving form UI with validation
- 🔄 In Progress: Expiry warning display (<30 days)
- ⚠️ Blocked: Need backend endpoint for expiry alerts
```

---

## 🔄 Iteration Cycle

1. **Week Start**: Orchestrator prioritizes next 3-5 tasks
2. **Daily**: Agents work on assigned tasks, update dashboard
3. **Week End**: Orchestrator reviews "What's Done", plans next week
4. **Milestone**: Update `PROJECT_SPECIFICATION.md` with new capabilities

---

## 📖 Reference

- Agent roles: `AGENTS.md`
- Locked rules: `RULES_OF_ENGAGEMENT.md`
- Current status: `PROJECT_DASHBOARD.md`
- Project spec: `../PROJECT_SPECIFICATION.md`
