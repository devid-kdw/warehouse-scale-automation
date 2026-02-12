# Changelog

All notable changes to the Warehouse Scale Automation project will be documented in this file.

Format: Each entry includes **Date**, **What Changed**, **Why**, **How to Test**, and **Commit/PR Reference**.

---

## [Unreleased]

### 2026-02-10 - Frontend Cleanup and Improvements (TASK-0017)
**What**: Critical fix for location ID, debug log removal, and UI reliability improvements.

**Why**: Align frontend with Backend (Rule 3) by standardizing location ID to 13, improve security by removing debug logs, and enhance UX with better receipt history and error tracking.

**Changes**:
- **Frontend (TASK-0017)**:
  - **Location ID**: Changed all hardcoded `location_id: 1` to `13` (Receiving, Draft Entry, Bulk Entry, and Types).
  - **Security**: Gated API client `console.log` statements behind `DEV` mode check in `client.ts`.
  - **Receipt History**: Added "Received By" column to display the name of the user who processed the receipt.
  - **Reliability**: Added a global `ErrorBoundary` component to catch and display UI crashes gracefully.
  - **Types**: Added `location_id` to `CreateDraftGroupPayload` and `user_name` to `ReceiptHistoryLine`.

**How to Test**:
- Open Bulk Entry or Receiving -> Submit -> Verify `location_id: 13` in network payload.
- View Receipt History -> Verify "Received By" column is visible.
- Check browser console in production build -> No `[API Client]` logs should appear.

**Ref**: TASK-0017, RULES_OF_ENGAGEMENT Rule 3

---

### 2026-02-10 - Backend Bugfixes and Hardening (TASK-0016)
**What**: Critical bug fixes for backend services, consistency improvements, and security hardening.

**Why**: Fix duplicate logic, resolve test failures, standardize location ID to 13, and improve error handling.

**Changes**:
- **Backend (TASK-0016)**:
  - **Location ID**: Changed default `location_id` from 1 to 13 across all services and APIs (Rule 3).
  - **Logic Fixes**: Removed duplicate batch ID resolution in `draft_group_service`.
  - **Error Handling**: Fixed `AttributeError` in inventory API handlers; migrated to global error handling to avoid flask-smorest schema stripping.
  - **Security & Consistency**: Removed legacy `require_token` decorator; standardized `actor_user_id` as integer.
  - **Idempotency**: Added `client_event_id` to `StockReceiveRequestSchema`.
  - **Tests**: Resolved 20+ test failures, including pre-existing JWT token identity and schema serialization issues.

**How to Test**:
- Run full test suite: `pytest backend/tests/ -v`.
- All 81 tests should pass.

**Ref**: TASK-0016

---

### 2026-02-07 - Final Fixes (v2.1)
**What**: Critical bug fixes for Consumables in Bulk Entry and Electron Security hardening.

**Why**: Fix blocking issue where Consumables required batch selection, and improve application security.

**Changes**:
- **Frontend (TASK-0014)**:
  - **Bulk Entry**: Consumables now hide Batch Select and show "System Batch (NA)".
  - **Security**: Disabled `nodeIntegration` in Electron to prevent renderer process risks.
- **Backend (TASK-0015)**:
  - **Schema**: `DraftGroupLineSchema` now allows `batch_id=null`.
  - **Service**: Auto-assigns "NA" system batch for consumables if `batch_id` is missing.
  - **Refactor**: Shared `batch_service` logic for system batch creation.

**How to Test**:
- Bulk Entry: Add Consumable -> Batch dropdown hidden -> Submit -> Success.
- Electron: App runs without console errors accessing Node APIs.

**Ref**: TASK-0014, TASK-0015

### 2026-02-07 - Inventory Hotfix (v2.1.1)
**What**: Backend serialization fixes for Inventory Summary.

**Why**: Fix `TypeError` when Marshmallow received Date objects for String fields, and ensure float precision for totals.

**Changes**:
- **API**: Explicit `float()` casting for `total_qty` calculation.
- **API**: Manual `.isoformat()` serialization for dates (`expiry_date`, `updated_at`).
- **Schema**: Updated `InventorySummaryItemSchema` to use `fields.String` for date fields.

**Ref**: Hotfix

---

### 2026-02-07 - Core Refinement v2
**What**: Backend and Frontend updates for stricter data integrity and better UX.

**Why**: Align with "Project Knowledge v1.0", improve receiving workflow (order numbers), and refine Operator/Admin draft experience.

**Changes**:
- **Backend (TASK-0010)**:
  - Added `order_number` to `Transaction` model with index and normalization.
  - Implemented strict Atomicity for Draft Group approval.
  - Implemented Receipt Grouping API logic.
  - Consumables logic: `is_paint=False` uses system batch "NA".
  - Migrations: `c8f64cf6440c_add_order_number_and_indexes.py`
  
- **Frontend (TASK-0011)**:
  - **Draft Entry**: Added Manual/Scale toggle (persisted) and non-invasive Barcode listener.
  - **Receiving**: Added `Order Number` field (required) and validation.
  - **Inventory**: Added tabs for Paint vs Consumables.
  - **UX**: Improved batch selection and error handling.

**How to Test**:
- Receiving: Submit without order number -> Error.
- Draft Entry: Toggle "Scale", refresh page -> stays "Scale".
- Migration: `flask db upgrade` maps new columns.

**Ref**: TASK-0010, TASK-0011

---

### 2026-02-04 - Draft Groups (Bulk Approval)
**What**: Implemented Draft Groups for atomic multi-line weigh-in draft operations.

**Why**: Enable users to approve or reject groups of drafts simultaneously with guaranteed data consistency and inventory checks.

**Changes**:
- **Backend**:
  - New `DraftGroup` model and relationship to `WeighInDraft`.
  - Service layer with row-level locking and atomic availability pre-checks.
  - New APIs for bulk creation and group approval/rejection.
  - Backward compatibility: v1 single-draft API auto-creates groups.
  - Manual migration with data backfill for existing drafts.
- **Verification**: 9 new tests covering atomic success, rollback logic, and precision.

**How to Test**: `pytest tests/test_draft_groups.py -v`

---

### 2026-02-04 - Article v1.2 & JWT Security Policy
**What**: Updated Article model with standard paint fields and tightened JWT security.

**Why**: Enforce data quality (units, manufacturer info) and ensure production security standards.

**Changes**:
- **Backend**:
  - `Article` model: Added `uom` (KG/L - required), `manufacturer`, `manufacturer_art_number`, `reorder_threshold`.
  - `ArticleSchema`: Validates `uom` (must be KG or L), deprecated `base_uom`.
  - Config: Updated JWT attributes (15 min access, 7 day refresh).
  
- **Frontend**:
  - Added `useAuth` hook for reactive auth state.
  - Updated API client endpoints and types (inferred from file list).

**How to Test**:
- Create article without `uom` -> Expect 400 Error.
- Create article with `uom='KG'` -> Success.
- Check `.env` for new JWT settings.

**Ref**: Decisions 2026-02-04

---

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
