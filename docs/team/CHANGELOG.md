# Changelog

All notable changes to the Warehouse Scale Automation project will be documented in this file.

Format: Each entry includes **Date**, **What Changed**, **Why**, **How to Test**, and **Commit/PR Reference**.

> [!NOTE]
> Older entries reflect historical implementation context.
> Current policy authority is:
> `RULES_OF_ENGAGEMENT.md` -> `DECISIONS.md` -> active task brief (`TASK-0020`).

---

## [Unreleased]

### TASK-0026 — Frontend v3 Phase 1: i18n, Layout, and Shell Foundation (2026-02-17)
- **What**: Implemented Croatian-first internationalization infrastructure, language switcher, and standardized layout tokens for wider content areas.
- **Changes**:
  - **i18n Infrastructure**:
    - Installed `react-i18next`, `i18next`, and `i18next-browser-languagedetector`
    - Created i18n configuration with 4 locales (hr, en, de, hu)
    - Croatian set as default language with localStorage persistence
    - Created translation files with approved terminology and full diacritics (č, ć, ž, š, đ)
  - **Language Switcher**:
    - New `LanguageSwitcher` component in app header
    - Dropdown menu with Hrvatski/English/Deutsch/Magyar options
    - Language selection persists across sessions
  - **App Shell Updates**:
    - Converted all hardcoded UI strings to translation keys
    - App title now shows "Skladišni Menadžer" (Croatian) by default
    - Sidebar navigation labels fully translated
    - User menu and access denied messages use i18n
  - **Layout Tokens**:
    - Created global CSS custom properties for content widths and gutters
    - Increased max content width to 1280px (from ~720px)
    - Reduced side gutters for wider usable space
    - Responsive breakpoints for tablet (768px) and desktop (1024px+)
    - Updated AppShell main padding for better spacing
- **Files Changed** (12 files):
  - Created: `i18n/index.ts`, `i18n/locales/{hr,en,de,hu}/common.json`, `components/LanguageSwitcher.tsx`, `styles/layout.css`
  - Modified: `App.tsx`, `Sidebar.tsx`, `main.tsx`, `package.json`
- **Verification**: `npm run build` passes cleanly (exit code 0)
- **How to Test**:
  - Run `npm run electron:dev`
  - Verify app starts in Croatian with "Skladišni Menadžer" title
  - Click language switcher and verify UI updates for all 4 languages
  - Refresh browser and verify selected language persists
  - Check content areas are visibly wider across screens
- **Ref**: TASK-0026, TASK-0021 (Phase 1)

### TASK-0027 — Frontend v3 Phase 2: Orders & Receiving UI (2026-02-17)
- **What**: Implemented Orders module (Narudžbe) and refactored Receiving workflow (Ulaz robe).
- **Changes**:
  - **Orders Module**:
    - Created `OpenOrders` and `ClosedOrders` list views
    - Created `OrderDetail` view with line management (add/remove/update)
    - Created `CreateOrder` form with auto-numbering support
    - Integrated with backend `api/orders` service
  - **Receiving UI**:
    - Refactored `Receiving` page to "Ulaz robe"
    - Added `delivery_note_number` (required) and `order_line_id` linking
    - Implemented conditional Batch/Expiry fields based on `has_batch`
    - Embedded `ReceiptHistory` list directly in receiving page
  - **Navigation**:
    - Created "Narudžbe" parent group
    - Removed standalone "Receipt History" and "Batches" routes
    - Updated RBAC to ensure Admin-only access for new modules
- **Files Changed**:
  - Created: `api/orders.ts`, `pages/Orders/{OpenOrders,ClosedOrders,OrderDetail,CreateOrder}.tsx`, `components/ReceiptHistoryList.tsx`
  - Modified: `App.tsx`, `Sidebar.tsx`, `pages/Receiving/index.tsx`, `i18n/locales/{hr,en}/common.json`
- **Verification**: `npm run build` passes cleanly
- **Ref**: TASK-0027

### Review Feedback — Robustness Fixes (2026-02-17)
- **receipt_number**: Replaced string-MAX with Python-side integer parsing (safe past 9999)
- **dedup fallback**: `identifikator_service.submit_missing_article_report` raises `AppError` if `.first()` returns None after IntegrityError rollback
- **order SQL**: `generate_order_number()` now uses Python-side parsing (works on SQLite + PostgreSQL)
- **error keys**: `InsufficientStockError` details use `required`/`available_stock`/`available_surplus`/`shortage` (removed `_kg` suffixes)
- **Verification**: 130/130 tests passing

### TASK-0026B — Backend Runtime Contract Stabilization (2026-02-17)
- **What**: Full decommission of legacy `quantity_kg` across all runtime code and tests. Canonical contract is now `quantity` + `uom`.
- **Breaking Changes (Frontend)**:
  - Draft/DraftGroup schemas: `quantity_kg` → `quantity`, `total_quantity_kg` → `total_quantity`
  - Approval response: `consumed_surplus_kg`/`consumed_stock_kg` → `consumed_surplus`/`consumed_stock`
  - Transaction schema: `quantity_kg` → `quantity` + `uom`
  - Inventory summary: primary keys are now `stock`/`surplus`/`total` (backward-compat `stock_qty`/`surplus_qty`/`total_qty` still emitted via schema)
- **Changes** (16 runtime files, 13 test files):
  - **Models**: Removed duplicate `batch_id` columns, renamed `DraftGroup.total_quantity_kg` → `total_quantity`
  - **Schemas**: Updated drafts, draft_groups, approvals, transactions, inventory, reports
  - **APIs**: All endpoints read `.quantity` and include `uom`
  - **Services**: `receiving_service` returns `previous_stock`, `draft_group_service` adds auto-naming, `validation` default field updated
  - **Seed/Tests**: All fixtures and assertions use `quantity` + `uom`
- **Backward Compat Retained**:
  - `reports.py`: dual-emit `quantity_kg` via `attribute='quantity'`
  - `inventory.py` schema: accepts legacy `quantity_kg` input
  - `draft_group_service.py`: fallback `get('quantity', get('quantity_kg'))`
- **Verification**: `compileall` clean, 126/130 tests pass (4 pre-existing failures unrelated to contract)
- **How to Test**: `cd backend && python3 -m pytest -v`

### 2026-02-17 - DEV/TEST Data Reset
- **What**: Full database reset and bootstrap to clean baseline.
- **Changes**:
  - Truncated all application tables via `reset_dev_db.py`.
  - Re-seeded default admin user `stefan` (password `ChangeMe123!`).
  - Re-seeded default Location 13.
- **Verification**: User count=1, Location count=1, Articles=0.

### 2026-02-17 - Orchestrator Backend Audit + Frontend Contract Realignment
- **What**: Orchestrator reviewed implemented backend v3 wave and aligned frontend tasks/prompt with actual backend contracts.
- **Changes**:
  - Added backend contract snapshot and review notes:
    - `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`
  - Updated locked rules/decisions for current contract and deprecation boundaries:
    - `docs/team/RULES_OF_ENGAGEMENT.md`
    - `docs/team/DECISIONS.md`
  - Updated frontend execution docs to use canonical implemented routes/contracts:
    - `docs/tasks/frontend-agent-tasks/PROMPT-frontend-agent-v3-wave.md`
    - `docs/tasks/frontend-agent-tasks/TASK-0027-frontend-v3-phase-2-orders-and-receiving-ui.md`
    - `docs/tasks/frontend-agent-tasks/TASK-0028-frontend-v3-phase-3-izlaz-and-approvals-ui.md`
    - `docs/tasks/frontend-agent-tasks/TASK-0029-frontend-v3-phase-4-skladiste-izvjestaji-identifikator.md`
  - Added dedicated backend follow-up task for full legacy quantity decommission:
    - `docs/tasks/backend-agent-tasks/TASK-0026A-backend-quantity-kg-decommission-and-remediation.md`
- **Verification**:
  - Static compile check passed (`python3 -m compileall app`).
  - Full pytest requires project DB environment (sandbox could not access local PostgreSQL).

### TASK-0026 — Backend v3 Phase 4: Remediation, Polish & Decommission (2026-02-17)
- **What**: Data integrity enforcement, unit-aware math hardening, missing report features, and decommission preparation for legacy `quantity_kg` model.
- **Changes**:
  - **Data Integrity**: Enforced `NOT NULL` on `Transaction.quantity` and `Transaction.uom` with historical backfill.
  - **Unit-Awareness**: Refactored `ApprovalService`, `ReceivingService`, `InventoryService`, and `DraftGroupService` for precise L/KG conversion using Article density.
  - **Decommission Prep**: Added migration and service groundwork toward removing legacy `quantity_kg` columns.
  - **Reporting**: Added Top-20 monthly consumers, Surplus Excel export, and aggregate stats for missing article reports.
  - **Hierarchy**: Refactored Inventory API for Article+Batch granularity.
  - **Safety**: Implemented lazy imports for `openpyxl` and `fpdf2` to prevent startup failures.
  - **API**: Added `Deprecation` and `Sunset` headers to legacy admin routes; registered matching routes under `/api/admin/identifikator`.
- **Migration**: 
  - `v3_p4_remed_v3_phase4_remediation.py` (Article.density + Transaction NOT NULL).
  - `v3_p4_decom.py` (DROP quantity_kg columns).
- **Tests**: 121 total (all core remediation tests passing).

### TASK-0024 — Backend v3 Phase 3: Outbound & Approvals (2026-02-17)
- **What**: Unit-aware drafting and approval workflow.
- **Changes**:
  - **Approvals**: Refactored `approve_draft` to be unit-aware, populating mandatory unit columns in transactions.
  - **Inventory Count**: Updated counts and shortage drafts to include units (defaulting to 'KG' for mass counts).
  - **Delta Logic**: Hardened inventory adjustments for unit-consistency.
- **Migration**: `v3_phase3_approvals.py` (legacy).

### TASK-0023 — Backend v3 Phase 2: Orders & Receiving (2026-02-17)
- **What**: Orders domain service, lifecycle automation, and unit-aware receiving linkage.
- **Changes**:
  - **Orders**: New `Order` and `OrderLine` models with status automation (Rule 12: all lines fulfilled → CLOSED).
  - **Auto-numbering**: `ORD-xxxx` generation with DB-unique constraint and service-level retry (Finding #3).
  - **API**: New `orders` blueprint (ADMIN-only) for CRUD, line removal, and list filtering.
  - **Receiving (v3)**: `receive_stock` is now unit-aware (Rule 2). Preferred params are `quantity` + `uom`.
  - **Ad-hoc Receiving**: `order_number` is now optional; ad-hoc requires a `note` (Rule 10).
  - **Receiving Traceability**: `delivery_note_number` is now mandatory for all receiving (Rule 11).
  - **Validation**: Strict receiving validation for line ↔ article match, line status, and order status (Finding #4).
  - **Deprecation**: Added `Deprecation` and `Sunset` headers to standalone `POST /api/batches` endpoint.
- **Migration**: `v3_phase2_orders.py` (orders/order_lines tables + FK on transactions).
- **Tests**: 112 total (was 103), all passing.

### TASK-0022 — Backend v3 Phase 1: Foundation & Migrations (2026-02-17)
- **What**: Schema foundations for v3.0 modules
- **Changes**:
  - Article: `has_batch`, `supplier_code`, `category` (12 normalized keys)
  - `uom_catalog` table — open-entry UOM persistence
  - Unit-aware `quantity` + `uom` columns on Stock, Surplus, Transaction, WeighInDraft
  - Hardware source fields on WeighInDraft (`scale_id`, `scanner_id`, `station_id`, `source_label`, `source_meta`)
  - Transaction receiving linkage fields (`delivery_note_number`, `order_line_id`)
  - Service logic switched from `is_paint` → `has_batch` (receiving, draft groups)
  - UOM validation: removed `OneOf(['KG','L'])`, replaced with open-catalog + normalization
  - Backward compat: `has_batch` derived from `is_paint` when not sent in API
  - `GET /api/uom` endpoint (any auth'd user)
- **Migration**: `v3_phase1_foundation.py` (additive, includes backfill + rollback)
- **Tests**: 103 total (was 87), all passing
### 2026-02-17 - v3.0 Implementation Planning Kickoff (TASK-0021 to TASK-0029)
**What**: Defined the next program version (`v3.0.0`) implementation package and decomposed execution into phased backend/frontend tasks.

**Why**: TASK-0020 owner feedback is finalized; delivery now requires strict phase sequencing (core first, then dependent modules) to reduce migration and contract risk.

**Changes**:
- Created `docs/tasks/TASK-0021-v3-implementation-master-plan.md` as the detailed v3 implementation roadmap.
- Created backend phase task briefs:
  - `docs/tasks/backend-agent-tasks/TASK-0022-backend-v3-phase-1-foundation-and-migrations.md`
  - `docs/tasks/backend-agent-tasks/TASK-0023-backend-v3-phase-2-orders-and-receiving.md`
  - `docs/tasks/backend-agent-tasks/TASK-0024-backend-v3-phase-3-outbound-and-approvals.md`
  - `docs/tasks/backend-agent-tasks/TASK-0025-backend-v3-phase-4-inventory-reports-identifier-and-decommission.md`
- Created frontend phase task briefs:
  - `docs/tasks/frontend-agent-tasks/TASK-0026-frontend-v3-phase-1-shell-i18n-layout.md`
  - `docs/tasks/frontend-agent-tasks/TASK-0027-frontend-v3-phase-2-orders-and-receiving-ui.md`
  - `docs/tasks/frontend-agent-tasks/TASK-0028-frontend-v3-phase-3-izlaz-and-approvals-ui.md`
  - `docs/tasks/frontend-agent-tasks/TASK-0029-frontend-v3-phase-4-skladiste-izvjestaji-identifikator.md`
- Added execution prompts for both agents:
  - `docs/tasks/backend-agent-tasks/PROMPT-backend-agent-v3-wave.md`
  - `docs/tasks/frontend-agent-tasks/PROMPT-frontend-agent-v3-wave.md`

**How to Test**:
- Verify all `TASK-0021` to `TASK-0029` files exist and are phase-ordered.
- Verify prompts include mandatory reading paths and dependency order.
- Verify `TASK-0021` reflects locked rules from `RULES_OF_ENGAGEMENT.md` and decisions from `DECISIONS.md`.

**Ref**: TASK-0020, TASK-0021, TASK-0022, TASK-0023, TASK-0024, TASK-0025, TASK-0026, TASK-0027, TASK-0028, TASK-0029

### 2026-02-17 - Documentation Governance Alignment (TASK-0020 Consolidation)
**What**: Documentation baseline aligned with finalized owner feedback from TASK-0020.

**Why**: Existing docs contained conflicting guidance (`is_paint`-coupled batch logic, KG-only assumptions, old module IA, outdated role notes) that would cause implementation drift.

**Changes**:
- **Governance**:
  - Updated `RULES_OF_ENGAGEMENT.md` with approved direction for unit-aware quantities, batch-tracking policy (`has_batch`), Orders/Receiving linkage, and refreshed RBAC matrix.
  - Rebuilt `DECISIONS.md` to include 2026-02-17 owner-approved decisions (Orders, Reports refactor, Article Identifikator, decommission paths).
- **Team Docs**:
  - Updated `AGENTS.md`, `AGENT_INSTRUCTIONS.md`, `QUICK_AGENT_BRIEFINGS.md`, `WORKFLOW.md`, `RELEASE_CHECKLIST.md`, `TESTING_AGENT_RULES.md`, `PROJECT_KNOWLEDGE.md`, `MIGRATIONS.md`, `ORCHESTRATOR.md`.
- **Planning Baseline**:
  - Confirmed `TASK-0020-ui-feedback-master-plan-input.md` as active redesign source.
  - Added archival-context disclaimers to historical task/status documents to prevent policy conflicts.
- **Root Docs**:
  - Updated `README.md`, `docs/README.md`, `PROJECT_SPECIFICATION.md` with authority order and redesign status notes.

**How to Test**:
- Verify no active governance doc contradicts `TASK-0020`.
- Confirm agent handoff docs point to `RULES` + `DECISIONS` + `TASK-0020`.
- Confirm historical docs are clearly marked as archival context.

**Ref**: TASK-0020

### 2026-02-17 - TASK-0020 Decision Closure Update (Owner Follow-up)
**What**: Applied owner responses for remaining pre-implementation decisions.

**Why**: Move from open questions to execution-ready planning baseline.

**Changes**:
- Updated `TASK-0020` remaining-decision statuses (language switcher in-wave, layout direction, timezone, approvals edit behavior, hardware identity fields, identifier lifecycle, statistics scope, order number format).
- Added `Terminology Input Required` list for final Croatian dictionary gaps.
- Updated `DECISIONS.md` with owner follow-up clarifications.
- Updated `RULES_OF_ENGAGEMENT.md` with timezone semantics.

**Ref**: TASK-0020

### 2026-02-12 - Frontend Contract, RBAC, and UX Alignment (TASK-0019)
**What**: Align frontend with backend API contracts, apply RBAC policy, and clean up documentation.

**Why**: Reports page sent unsupported query params, Draft Group detail mapped wrong response field, and OPERATOR inventory access was inconsistent with locked rules.

**Changes**:
- **Frontend (TASK-0019)**:
  - **Reports**: Fixed query params to use `tx_type`, `from`/`to` (ISO), `limit`/`offset`. Updated type filter options to match backend enum.
  - **Draft Group Detail**: Changed `group.lines` → `group.drafts` to match backend schema.
  - **Inventory**: Added safe `is_paint` fallback (`undefined` → paint). OPERATOR read-only mode hides admin actions.
  - **RBAC**: `/inventory` route now `RequireAuth` (OPERATOR can view). Sidebar updated.
  - **Types**: Added `TransactionQueryParams`, `drafts` on `DraftGroup`, `is_paint` made optional on `InventoryItem`.
  - **README**: Replaced obsolete API token/actor ID instructions with JWT login flow.

**How to Test**:
- Reports: apply tx_type + date filters, verify results.
- Draft Group: open detail modal, verify lines render.
- Inventory: OPERATOR login → view only (no action buttons). ADMIN → full actions.
- Build: `npm run build` passes.

**Ref**: TASK-0019, DECISIONS.md 2026-02-12 RBAC Clarification

---

### 2026-02-12 - Backend Contract, RBAC & Documentation Alignment (TASK-0018)
**What**: RBAC enforcement on reports, inventory RBAC relaxed for OPERATOR, API contract fixes, and documentation sync.

**Why**: Align backend with locked RULES_OF_ENGAGEMENT rules, fix frontend contract gaps, and resolve policy conflicts across docs.

**Changes**:
- **RBAC**: Reports endpoints now require ADMIN role (403 for OPERATOR). Inventory summary allows OPERATOR per Rule 12.
- **Transaction Fix**: `from` query filter was broken due to Marshmallow `data_key` mapping (`from` → `from_`).
- **Contract**: Inventory summary now includes `is_paint` field required by frontend tabs.
- **Aliases**: Case-insensitive uniqueness and lookup (strip + uppercase normalization).
- **Auth**: Login failures return `INVALID_CREDENTIALS` instead of generic `INVALID_TOKEN`.
- **Docs**: Fixed refresh token lifetime (30d → 7d), location ID, and RBAC descriptions in README and DECISIONS.md.

**How to Test**:
- `pytest backend/tests/ -v` — all 87 tests pass.
- Login as OPERATOR → call `/api/reports/transactions` → expect 403.
- Call `/api/inventory/summary` → each item has `is_paint`.

**Ref**: TASK-0018

---

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
