# Changelog

All notable changes to the Warehouse Scale Automation project will be documented in this file.

Format: Each entry includes **Date**, **What Changed**, **Why**, **How to Test**, and **Commit/PR Reference**.

---

## [Unreleased]

### 2026-02-04 - Agent Documentation Infrastructure
**What**: Created comprehensive documentation system for multi-agent coordination.

**Why**: Enable clear agent boundaries, testing protocols, and reduce confusion when assigning tasks to Frontend, Backend, and Testing agents.

**Changes**:
- Created `docs/team/TESTING_AGENT_RULES.md` - Testing agent protocol (320 lines)
  - Manual browser testing workflow
  - Test report format and bug severity guidelines
  - Application access methods (Electron vs Browser: http://localhost:5173)
  - Required reading checklist
  
- Created `docs/team/AGENT_INSTRUCTIONS.md` - Full instructions for all 3 agents
  - Frontend Agent: boundaries, tech stack, RBAC integration, quality gates
  - Backend Agent: code standards, transaction types, RBAC enforcement
  - Testing Agent: access methods, credentials, test patterns
  
- Created `docs/team/QUICK_AGENT_BRIEFINGS.md` - Copy-paste ready briefings
  - One briefing per agent type for task assignment
  - Quick reference for orchestrator
  
- Created `docs/team/DEVELOPMENT_SETUP.md` - Complete setup guide
  - Correct Python commands (pip3, python3)
  - Troubleshooting section (5 common errors)
  - Verification steps and test data management
  
- Updated `README.md`:
  - Simplified Quick Start with accurate commands
  - Added links to all new documentation
  - Fixed Python/pip commands (python3, pip3)

**How to Test**: N/A - Documentation only

**Ref**: Orchestrator setup

---

### 2026-02-03 - Receiving Workflow Implementation
**What**: Implemented stock receiving (INBOUND) workflow with `POST /api/inventory/receive` endpoint.

**Why**: Enable admins to record incoming stock deliveries with proper batch handling and audit trail.

**Changes**:
- Added `TX_STOCK_RECEIPT` transaction type to `Transaction` model
- Created `receiving_service.py` with atomic batch/stock handling
- Added `StockReceiveRequestSchema` and `StockReceiveResponseSchema` with Decimal fields
- Added `POST /api/inventory/receive` endpoint (ADMIN-only)
- Created 11 tests in `test_receiving.py` covering success, validation, and audit scenarios

**Key Features**:
- Decimal math with `ROUND_HALF_UP` (no floating point errors)
- Batch auto-creation if doesn't exist
- Expiry date backfill (NULL → set) with conflict detection (409)
- Lock order: Batch → Stock (prevents deadlocks)
- Full audit trail via `STOCK_RECEIPT` transaction

**How to Test**: `pytest tests/test_receiving.py -v` (11 tests pass)

**Ref**: Backend Agent implementation

---

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
- **Stock receiving workflow** (inbound goods)

### Known Limitations
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
