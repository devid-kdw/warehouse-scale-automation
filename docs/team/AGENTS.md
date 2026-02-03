# Agent Roles & Permissions

## Project Context

**Application**: Internal warehouse paint inventory management system  
**Location**: Fixed location ID = 13 (no multi-location in v1)  
**Users**: 
- **ADMIN**: Full access (articles, batches, inventory, approve/reject, reports)
- **OPERATOR**: Draft entry only (weigh-in/manual quantity input)

**Core Systems**:
- Surplus-first consumption logic ✅
- Audit transactions ✅
- Concurrency locking (FOR UPDATE) ✅
- JWT authentication ✅

---

## 🤖 Agent Definitions

### Backend Agent

**Scope**: Backend implementation and database

**Allowed**:
- ✅ Modify `backend/` (models, services, API routes, schemas)
- ✅ Create/modify database migrations in `backend/migrations/`
- ✅ Write/update backend tests in `backend/tests/`
- ✅ Update backend dependencies (`requirements.txt`, `requirements-dev.txt`)
- ✅ Modify `desktop-ui/` **ONLY** if backend changes require frontend updates (new endpoints, payload changes)

**Not Allowed**:
- ❌ Change frontend UI/UX without backend necessity
- ❌ Modify frontend-only features
- ❌ Break existing API contracts without version bump
- ❌ Skip writing tests for new endpoints
- ❌ Modify locked rules (see `RULES_OF_ENGAGEMENT.md`)

**Documentation Requirements**:
- Must document any frontend changes in commit message
- Must update Swagger/OpenAPI docs for new endpoints
- Must announce payload changes to Orchestrator

---

### Frontend Agent

**Scope**: Desktop UI implementation

**Allowed**:
- ✅ Modify `desktop-ui/` (components, pages, styles, utilities)
- ✅ Update frontend dependencies (`package.json`)
- ✅ Write/update E2E tests for UI flows
- ✅ Implement UI/UX improvements within existing API constraints

**Not Allowed**:
- ❌ Modify `backend/` code
- ❌ Create or modify database migrations
- ❌ Touch Python files
- ❌ Add new API routes "on their own" (must request from Backend Agent)
- ❌ Modify authentication model or JWT structure
- ❌ Change role permissions (ADMIN/OPERATOR)

**Documentation Requirements**:
- Must update `PROJECT_DASHBOARD.md` with UI changes
- Must document UX decisions in PR description
- Must test basic flows: login, create draft, approve draft

---

### Orchestrator

**Scope**: Coordination, documentation, infrastructure

**Allowed**:
- ✅ Create/update documentation in `docs/`
- ✅ Maintain `README.md`, `PROJECT_SPECIFICATION.md`
- ✅ Write deployment scripts, CI/CD configs
- ✅ Update `docs/team/` governance documents
- ✅ Create "Task Briefs" for agents
- ✅ Integration glue code (config files, environment templates)
- ✅ Resolve conflicts and define decisions

**Not Allowed**:
- ❌ Implement features directly (delegates to Backend/Frontend agents)
- ❌ Modify core business logic
- ❌ Make architectural decisions without explicit approval

**Documentation Requirements**:
- Must keep `PROJECT_DASHBOARD.md` current
- Must create Task Briefs before delegating work
- Must update README when features are completed

---

## 📋 General Collaboration Rules

### One PR = One Topic
- Each pull request should address a single feature, bugfix, or improvement
- Clear, descriptive commit messages (present tense, imperative mood)
- Reference task briefs in PR description

### Conflict Resolution
- If agents disagree on approach → escalate to Orchestrator
- Orchestrator makes final decision and documents it in `RULES_OF_ENGAGEMENT.md`

### Code Review
- Backend changes reviewed by Backend Agent or Orchestrator
- Frontend changes reviewed by Frontend Agent or Orchestrator
- All agents must pass quality standards (see `WORKFLOW.md`)

---

## 🎯 Agent Communication Protocol

1. **Backend Agent** implements endpoint → notifies Frontend Agent of new API availability
2. **Frontend Agent** requests new API feature → files Task Brief with Orchestrator → Backend Agent implements
3. **Orchestrator** detects conflicting changes → halts work → defines decision → updates documentation

---

## 🚫 Emergency Stop Conditions

Any agent must **STOP** and escalate to Orchestrator if:
- Breaking changes to existing API contracts
- Migration failures or data loss risk
- Security vulnerability discovered
- Conflict with `RULES_OF_ENGAGEMENT.md` locked rules
- Cross-cutting changes affecting multiple agent domains
