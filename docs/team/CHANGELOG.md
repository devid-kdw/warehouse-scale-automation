# Changelog

All notable changes to the Warehouse Scale Automation project will be documented in this file.

Format: Each entry includes **Date**, **What Changed**, **Why**, **How to Test**, and **Commit/PR Reference**.

---

## [Unreleased]

### 2026-02-03 - Orchestration Infrastructure Setup
**What**: Created documentation structure for change tracking, decision logging, and status reporting.

**Why**: To maintain clear project history, facilitate team coordination, and ensure Stefan always knows project state.

**Changes**:
- Created `docs/team/` folder for team documentation (CHANGELOG, DECISIONS, MIGRATIONS, AGENTS, RELEASE_CHECKLIST)
- Created `docs/status/` folder for status reports
- Created `docs/tasks/` folder for task briefs
- Established documentation standards and commit conventions

**How to Test**: N/A - Documentation only

**Ref**: Initial setup

---

## [v1.1.0] - Current Version

### Features Implemented
- JWT authentication with role-based access (ADMIN/OPERATOR)
- Draft-based approval workflow (weigh-in → approve → stock update)
- Inventory count with surplus/shortage handling
- Batch tracking with expiry dates
- Transaction audit trail
- Inventory summary view with expiry warnings
- Article and batch management

### Known Limitations
- **No receiving/inbound workflow** - cannot add new stock arrivals
- Transaction reports UI needs improvement
- Single-location only (location_id=1, code="13")

---

## Version History

### v1.1.0 (Current)
- Initial production-ready implementation
- Backend: Flask + PostgreSQL + JWT auth
- Frontend: Electron + React + Mantine UI
- Database migrations tracked via Alembic

---

## Commit Convention

Use these prefixes for all commits:
- `docs:` - Documentation changes only
- `chore:` - Build, config, dependencies (no code changes)
- `backend:` - Backend code changes (Python, API, models, services)
- `ui:` - Frontend code changes (React, Electron, UI components)
- `security:` - Security-related changes
- `refactor:` - Code refactoring without feature changes
- `fix:` - Bug fixes
- `feat:` - New features

Example: `backend: add STOCK_RECEIPT transaction type`
