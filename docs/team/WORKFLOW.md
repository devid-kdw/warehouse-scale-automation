# Development Workflow

Standard process for implementation, verification, and documentation governance.

---

## 1. Task Creation (Orchestrator)

Each task brief must define:
1. Goal
2. Scope (in/out)
3. Acceptance criteria
4. Test plan
5. Agent assignment
6. Dependencies and blockers

Task files live in `docs/tasks/`.

---

## 2. Implementation Flow

### Backend-first when contract/model changes are required
- models
- migrations
- services
- APIs/schemas
- tests

### Frontend follows stable contract
- routes/pages/components
- role-aware UX
- i18n keys and Croatian baseline strings
- integration with backend endpoints

### Testing
- acceptance criteria execution
- RBAC checks
- regression checks
- audit validation

---

## 3. Quality Gates

### Backend
- pytest pass
- migration pass
- no integrity regressions
- API docs updated

### Frontend
- build pass
- no major console/runtime errors
- role visibility/actions correct

### Docs
- changelog updated
- decisions updated for policy changes
- migration log updated for schema changes

---

## 4. Conflict Resolution

If docs conflict, precedence is:
1. `docs/team/RULES_OF_ENGAGEMENT.md`
2. `docs/team/DECISIONS.md`
3. active task brief (currently `TASK-0020` for redesign wave)
4. historical docs

Any locked-rule change requires explicit owner approval and documentation updates.

---

## 5. Definition of Done

Done means:
- acceptance criteria met,
- quality gates passed,
- documentation updated,
- unresolved risks explicitly logged.

---

Last Updated: 2026-02-17
