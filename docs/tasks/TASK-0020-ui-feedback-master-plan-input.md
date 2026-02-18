# TASK-0020: UI Feedback Master Log (Plan Input)

**Created**: 2026-02-12  
**Owner**: Orchestrator  
**Status**: Input Complete (promoted to implementation plan `TASK-0021`)

---

## Purpose

Capture business feedback per screen, translate it into implementable technical requirements, and flag any conflict with locked project rules before implementation planning.

This file is the source input for creating implementation task briefs for Frontend/Backend agents.
Implementation execution plan is documented in `docs/tasks/TASK-0021-v3-implementation-master-plan.md`.

---

## Governance Guardrails (Must Stay Valid)

1. `docs/team/RULES_OF_ENGAGEMENT.md` is LOCKED and has priority over non-locked docs.
2. If a requested UI change impacts locked business logic, mark it as **Decision Required** before implementation.
3. UI copy/language changes must not alter backend API contracts, enum values, audit semantics, RBAC checks, or transaction logic.

---

## Global Requests (Apply Across Entire UI)

### G-001: Full Croatian UI + Future Multi-language Support

**Business requirement (MUST)**  
Entire UI should be in Croatian now. Code remains in English. Later, language switch should support Croatian, English, German, and Hungarian.

**Technical translation**
- Introduce i18n layer for all user-facing strings (pages, forms, nav, toasts, validation, empty states).
- Keep internal code identifiers, API payload keys, and backend enums in English.
- Use translation keys in code (English key naming), with `hr` as default active locale.
- Prepare locale resources: `hr` now, scaffold `en/de/hu` for later rollout.

**Risk / caution**
- Large cross-cutting frontend change (all screens), high regression risk if done ad-hoc.
- Must include fallback strategy for missing keys and a phased migration plan.

---

### G-002: Wider Content Area on Screens

**Business requirement (MUST)**  
Reduce wasted horizontal space between left menu and page content. Form areas should be wider so full text/input is visible.

**Technical translation**
- Review page container sizing strategy (`Container size=\"sm\"` is too narrow on key screens).
- Introduce consistent layout width tokens per screen type (form/list/detail) and responsive breakpoints for tablet/desktop.
- Keep readability on tablets; avoid fixed ultra-wide fields on small widths.

**Risk / caution**
- Broad UX change affecting many screens; requires visual QA sweep after implementation.

---

### G-003: Multi-Unit Domain Semantics (Confirmed by Owner)

**Business requirement (MUST)**  
System must support true multi-unit semantics (`kg`, `l`, `kom`, `pak`, and future custom units/categories), with values persisted in database and reflected consistently in UI/API.

**Technical translation**
- Evolve data model from `quantity_kg`-centric semantics to unit-aware quantity semantics.
- Define unit model strategy:
  - controlled list + optional custom units, or
  - fully open text/category model with governance.
- Update validation, reporting, transaction display, import/export, and audit views to include unit context.
- Preserve migration path from existing `quantity_kg` data.

**Risk / caution**
- This is a system-wide refactor (backend, frontend, tests, docs, locked rules, migrations).
- Requires explicit rule/version updates in `RULES_OF_ENGAGEMENT.md` and `DECISIONS.md` before implementation.

---

## Screen Feedback Log

### S-001: Draft Entry Screen (`/drafts/new`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Operational context**: Tablet UI for paint operators receiving measured weight from scale/backend integration.

#### Requested Changes (MUST)

1. Title text:
   - From: `Manual Weigh-In Entry`
   - To: `Automatski unos`
2. Remove subtitle text:
   - `Create new weight drafts. Entries will be pending approval.`
3. Remove `Single Entry` / `Bulk Entry (Admin)` tab switch from this screen.
4. Entry mode default must be `scale` (manual remains fallback only).
5. `Client Event ID` must not be visible on screen.
6. Remove `My Recent Drafts` block from this screen.

#### Technical Translation for Developers

1. Keep `/drafts/new` focused on single operator flow (automatic scale-first input).
2. Keep bulk workflow accessible via dedicated bulk screen/route only (admin flow), not as tab inside Draft Entry.
3. Change qty mode initialization fallback from `'manual'` to `'scale'` when no local preference exists.
4. Keep idempotency support active:
   - `client_event_id` should still be generated/sent in payload (hidden field / internal state), or safely server-generated if backend explicitly guarantees equivalent behavior.
5. Remove recent drafts query/render logic from this page to simplify operator UX.
6. Apply Croatian copy for all visible strings on this screen as part of G-001.

#### Conflict Check (Locked Rules / Existing Decisions)

- **No locked-rule conflict** for title/copy/layout/tab visibility changes.
- **Important caution (Rule 10, idempotency)**: Hiding `Client Event ID` in UI is valid; removing idempotency behavior is not valid.
- **Important compliance note (Rule 3, location fixed = 13)**: UI should not expose location selector in v1. Current screen still shows `Location ID`; this should be removed/hidden in implementation planning.
- **Behavior clarification needed**: Draft Entry currently persists mode in local storage. Requirement "default = scale" must be interpreted as either:
  - first load default only, or
  - forced scale default on every screen open/session.
- **Documentation drift to resolve**: older task specs (`TASK-0002`, `TASK-0011`) required bulk tab inside Draft Entry. New feedback supersedes that UX requirement and should be recorded as latest direction in upcoming implementation task(s).

#### Suggested Acceptance Criteria (for future implementation task)

1. Draft Entry header shows only `Automatski unos` (no subtitle).
2. No entry tabs are shown on `/drafts/new`.
3. Default mode is `scale` on first load (without prior user setting).
4. `Client Event ID` is not visible but successful submit still includes stable idempotency behavior.
5. `My Recent Drafts` is not rendered on this screen.
6. Location input is not visible (location remains fixed to 13 by system logic).

---

## Remaining Decisions Before Implementation Planning

1. Croatian terminology dictionary for all modules (final canonical labels and glossary for i18n keys).
   - **Status**: Pending owner completion (owner requested full term list for fill-in).
   - **Language quality rule**: Croatian UI strings must use full diacritics (`č`, `ć`, `ž`, `š`, `đ`; and `dž` where applicable).
2. Language switcher (`hr/en/de/hu`) rollout phase.
   - **Status**: Decided - include in current implementation wave.
3. Global layout tokens (container widths and breakpoints for tablet/desktop).
   - **Status**: Decided - standardize shared widths and reduce side margins (left menu gap and right page margin) to widen content area across screens.
   - **Owner note**: tablet profile primarily uses `Automatski unos`; tablet breakpoints still required by frontend design.
4. Draft Entry mode persistence policy.
   - **Status**: Decided - `scale` is first-load default (tablet session is long-lived).
5. Multi-unit model strategy.
   - **Status**: Decided - open UOM entry; new units persist into catalog; operator/admin can still enter previously unseen unit.
6. Inventory `Inspect article` contract ownership.
   - **Status**: Decided - backend should own computed inspect payload (batch quantities, totals, last received/issued/activity); frontend primarily renders.
7. Approvals daily-list day-boundary (local warehouse day vs UTC day).
   - **Status**: Decided - timestamps are stored in UTC; daily list grouping is by `Europe/Berlin` operational day (Hamburg context), with future location-based timezone extensibility.
8. Approvals aggregated edit propagation.
   - **Status**: Decided - pre-approval edits overwrite pending draft values; no separate correction transaction is created before approval because stock is not yet impacted.
9. Future hardware identity canonical fields.
   - **Status**: Decided - standardize broad source identity fields now (`scale_id`, `scanner_id`, `station_id`, `source_label`, optional hardware metadata) for future integrations.
10. Article Identifikator report lifecycle details.
   - **Status**: Decided - queue view is hosted under `Izvještaji` as dedicated sub-view for identifier queries; identical reports are deduplicated/merged; admin can mark `Resolved`; report is closed only via explicit close action.
11. Statistics detail formulas.
   - **Status**: Decided - implement all proposed baseline statistics options in first iteration; do not split lists by UOM.
12. Orders auto-number format.
   - **Status**: Decided - `ORD-xxxx` numeric padded format.

### Terminology Input Required (Owner Fill-In)

1. `app.title`  
   - EN: `Warehouse Ops`  
   - HR: `Skladišni Menadžer`
2. `status.disconnected`  
   - EN: `Disconnected`  
   - HR: `Odspojen`
3. `identifier.search`  
   - EN: `Search by name/code/alias`  
   - HR: `Pretraži po imenu/kodu/alijasu`

---

### S-002: Bulk Entry Screen (`/drafts/bulk`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Decision status**: Owner decisions recorded (major refactor accepted)

#### Requested Changes (MUST)

1. Screen/page name:
   - From: `Bulk Entry`
   - To: `Izlaz`
2. Header field replacement:
   - Replace `Group Name (Optional)` with system-assigned `Broj izlaza` (format example: `0001`, `0002`, ...).
   - Add separate group-level text field for full description/comment (`Opis izlaza` / napomena).
3. Table columns:
   - `Article` should show only article number (not full "number + name").
   - Rename to `Article Number` / `Broj artikla`.
   - Full article name should appear in `Description`.
4. While entering article number:
   - Description area should offer candidate full names for matching prefixes until full article number is entered.
5. Remove `Mfr` column from this screen.
6. `UOM` remains visible and read-only in this screen (comes from selected article master data).
7. Batch behavior:
   - For articles without batch tracking, batch field should not be shown.
   - For batch-tracked articles, batch dropdown is shown only for that row/article.
   - Batch column should be moved after quantity column.
8. Quantity column:
   - Rename from `Qty (KG)` to `Količina` (remove KG suffix).
9. Remove line-level `Note` column.
   - Note/comment should exist only at group (`Izlaz`) level.

#### Technical Translation for Developers

1. Route/menu/page copy update to Croatian naming (`Izlaz`) as part of G-001.
2. Split header semantics:
   - Display a system-generated outbound reference (`receipt_number`, UI label `Broj izlaza`) as read-only.
   - Add editable group-level `description`/`comment` field.
3. Rework article selector UX:
   - Input/search by `article_no` first.
   - Keep description field as resolved article description.
   - Implement prefix suggestions behavior for partially typed article numbers.
4. Remove manufacturer column from row model and table rendering.
5. Keep UOM read-only from selected article metadata; do not allow edit on this screen.
6. Reorder columns to: `Loc | Broj artikla | Description | UOM | Količina | Batch (conditional) | Actions`.
7. Remove `line.note` from row UI and payload usage (temporary backward-compat as null/empty only if needed).
8. Transition batch behavior from `is_paint` proxy to explicit article batch-tracking flag (`has_batch`):
   - if `has_batch === false`, do not render batch selector,
   - if `has_batch === true`, render batch selector with row-scoped options.

#### Conflict Check (Locked Rules / Existing Decisions)

- **Terminology conflict resolved by owner**: outbound flow label is `Izlaz` (not `Primka`).
- **Rule 11 / audit safety**: Converting line note into only group note is acceptable, but group-level note must remain auditable in backend response/storage.
- **Major rule impact (confirmed by owner)**: true multi-unit semantics goes beyond UI; current locked rules and contracts use `quantity_kg` assumptions.
- **No conflict** with stock/surplus logic as long as this screen still creates draft groups and does not directly add stock.

#### Backend Dependency / Owner Decisions (2026-02-12)

1. **Receipt number model**: confirmed
   - Implement new `receipt_number` field with migration + sequence allocation (do not derive from `draft_group.id`).
2. **Data reset authorization**: confirmed
   - Existing data is test-only; purge/reset is allowed to simplify migration rollout.
3. **Group description field**: required
   - Add separate persisted field for group-level description/comment (distinct from identifier).
4. **Batch tracking rule basis**: confirmed by owner
   - `Has Batch` is a more general business dimension than `is_paint`.
   - Introduce explicit article field (`has_batch` / `is_batch_tracked`) and migrate rules from `is_paint`-coupled behavior.
   - Keep `is_paint` only for product categorization where needed (paint/consumable views), not for mandatory batch requirement.
5. **Quantity unit semantics**: confirmed major refactor
   - Implement true unit-aware semantics and persistence across system (not just relabel `Qty (KG)`).
   - Requires coordinated updates in backend models/schemas/services/reports/tests/docs and locked-rules documentation.

#### Suggested Acceptance Criteria (for future implementation task)

1. Screen is labeled `Izlaz` in sidebar and page header.
2. User cannot manually edit outbound number; system assigns and displays `Broj izlaza`.
3. Group-level description is editable and stored.
4. Article column accepts/searches by article number only; description is displayed separately.
5. Manufacturer column is removed.
6. Quantity label is `Količina` (without KG).
7. Batch selector appears only for batch-tracked rows and is placed after quantity.
8. Line-level note column is removed; note is only at group level.
9. Backend persists and exposes `receipt_number` and group description fields.

---

### S-003: Receive Stock Screen (`/receiving`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner
**Owner clarification**: `is_paint` batch logic should be generalized to `has_batch` because non-paint materials can also be batch-tracked.

#### Requested Changes (MUST)

1. Screen/page naming and module hierarchy:
   - Rename screen from `Receive Stock` to `Ulaz robe`.
   - This screen should become a sub-item under future parent module `Narudžbe (Orders)` (module details to be specified later).
2. Remove subtitle/help text under page title:
   - Remove `Add new inventory to the warehouse. Requires Admin privileges.`
3. Article inputs:
   - First field should be article number input/selector.
   - Add separate `Article` field below to show resolved article name/description.
4. `Order Number` remains and will integrate with future Orders module.
5. Batch/expiry UX:
   - Replace direct `Batch Code` field with checkbox `Has Batch` (`Ima šaržu`).
   - Show batch input only when checkbox is checked.
   - Keep `Expiry Date`, but visually/UX-wise tie it with batch section.
6. Quantity label:
   - Change `Quantity (kg)` to `Količina` (remove kg suffix).
7. `Note` field remains.

#### Technical Translation for Developers

1. Update sidebar/menu labels and page title to Croatian naming (`Ulaz robe`) as part of G-001.
2. Keep receiving route ADMIN-only unless explicit RBAC change is requested.
3. Rework article selection UX:
   - primary lookup by `article_no`,
   - secondary read-only display of resolved article description/name.
4. Introduce conditional batch section with explicit toggle:
   - `has_batch` checkbox controls visibility/required state of `batch_code` and batch-linked expiry handling in UI.
5. Group batch + expiry fields in same visual block/card to emphasize dependency.
6. Keep `order_number` as required and prepare future relation to Orders module entity.
7. Keep note at receipt header level (as currently modeled in transaction meta/batch note usage).

#### Conflict Check (Locked Rules / Existing Decisions)

- **Terminology/IA change only**: `Receive Stock` -> `Ulaz robe` is safe; parent module `Narudžbe` is structural UI/navigation change.
- **Owner clarification recorded (batch logic)**:
  - `is_paint` logic should be generalized into explicit `has_batch` article capability.
  - This reduces conceptual conflict, but still requires backend model/service/schema/test refactor because current code enforces batch/expiry via `article.is_paint`.
- **Decision impact (expiry policy)**:
  - Existing decision says expiry is required for paint batches.
  - With `has_batch` model, expiry requirement should follow `has_batch` (or explicit batch policy), not paint classification.
- **Migration warning**:
  - Existing flows that auto-force `NA` for non-paint must be redefined for non-paint but batch-tracked materials (example given: kit).

#### Backend Dependency / Decision Required

1. **Orders module dependency**:
   - Define future `Orders` module scope and relationship to receiving records (`order_number` today, potential order entity tomorrow).
2. **Batch-toggle semantics**:
   - Owner decision: `Has Batch` should be article-master driven (generalized from `is_paint`), not an arbitrary per-transaction override.
   - Implement explicit article field (`has_batch` / `is_batch_tracked`) and bind receiving UI behavior to that field.
3. **Expiry requirement alignment**:
   - Update receiving service rules and decisions so expiry policy follows batch-tracking semantics, not paint semantics.
4. **UOM / quantity semantics alignment**:
   - Receiving currently stores `quantity_kg`; G-003 already confirms system-wide unit-aware refactor is required.
   - This screen should align with that refactor plan instead of one-off label-only change.

#### Suggested Acceptance Criteria (for future implementation task)

1. Screen and sidebar label show `Ulaz robe`.
2. `Ulaz robe` is positioned as child item under `Narudžbe` navigation group (once module scaffold exists).
3. Subtitle under title is removed.
4. Article number is entered/selected separately from article description display.
5. Batch section is visible/required based on article `has_batch` value (and hidden when `has_batch=false`).
6. Expiry field is visually coupled with batch details.
7. Quantity field label is `Količina`.
8. Note field remains available and persisted.

---

### S-004: Receipt History Screen (`/inventory/receipts`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner

#### Requested Changes (MUST)

1. Remove standalone `Receipt History` screen from navigation and routing.
2. Move receipt history functionality into `Ulaz robe` (`/receiving`) as embedded section (`Povijest ulaza`).
3. Keep listing of receipts (primke/ulazi) but without separate full page.

#### Technical Translation for Developers

1. Frontend IA/navigation:
   - Remove sidebar item `Receipt History`.
   - Remove dedicated route/page mount for `/inventory/receipts` (or keep hidden alias redirect only if needed for backward compatibility).
2. `Ulaz robe` page composition:
   - Add integrated history block under receiving form (or as second tab/accordion panel within same page).
   - Reuse existing receipt history query/API (`GET /api/inventory/receipts`) and rendering components where possible.
3. UX behavior:
   - After successful receiving submit, refresh both form-relevant queries and embedded history list.
   - Preserve ability to inspect grouped receipt lines/details inside `Ulaz robe`.

#### Conflict Check (Locked Rules / Existing Decisions)

- **No locked-rule conflict**: this is information architecture/UI consolidation; receiving workflow remains ADMIN-only and still the only inbound stock path.
- **Data/audit safety**: do not remove backend receipt history endpoint; only relocate frontend access pattern.
- **Module alignment**: change is consistent with planned `Narudžbe` parent module and `Ulaz robe` consolidation.

#### Backend Dependency / Decision Required

1. No mandatory backend contract change required if existing `/api/inventory/receipts` endpoint remains unchanged.
2. Optional future enhancement (non-blocking):
   - Add pagination/filter parameters to receipt history endpoint if embedded list grows large in production.

#### Suggested Acceptance Criteria (for future implementation task)

1. No standalone `Receipt History` menu item is visible.
2. Navigating to `Ulaz robe` shows receiving form plus embedded `Povijest ulaza`.
3. Embedded history shows grouped receipt entries and line details equivalent to prior standalone screen.
4. Submitting new receipt updates embedded history without manual page reload.

---

### S-005: Inventory Screen (`/inventory`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Owner clarifications recorded**:
- `Supplier` and `Manufacturer` are one logical model field for now (`supplier/manufacturer`) with no DB migration.
- Use `Last activity` (issued or received), not `Last issue`.
- Category model should be implemented to match requested taxonomy.
- `Edit article` and `Add article` remain ADMIN-only.

#### Requested Changes (MUST)

1. Rename screen/page:
   - `Inventory` -> `Skladište`
   - `Inventory Overview` -> `Pregled artikala`
2. Keep search bar.
3. Replace current `Paint Articles / Consumables` tabs with category filter:
   - Label: `Filtriraj kategorije`
   - Backend category keys in English, UI labels in Croatian.
4. Add record-state filter controls on inventory screen:
   - `Active` / `Inactive` / `All`
   - Replace old wording `Archived` with `Inactive` in UI.
   - Marking article as `Inactive` should perform existing archive behavior (`is_active = false`).
5. Category set (EN key -> HR UI label):
   - `equipment_installations` -> `Postrojenja / Oprema`
   - `safety_equipment` -> `Zaštitna oprema`
   - `operational_supplies` -> `Operativni materijal`
   - `spare_parts_small_parts` -> `Rezervni dijelovi / Sitni dijelovi`
   - `auxiliary_operating_materials` -> `Pomoćni i potrošni materijal`
   - `assembly_material` -> `Montažni materijal`
   - `raw_material` -> `Sirovine` (paint belongs here; separate paint category should not exist)
   - `packaging_material` -> `Ambalažni materijal`
   - `goods_merchandise` -> `Roba`
   - `maintenance_material` -> `Materijal za održavanje`
   - `tools_small_equipment` -> `Alati i sitna oprema`
   - `accessories_small_machines` -> `Dodatna oprema za male strojeve`
6. Filter behavior:
   - Record-state filter (`Active/Inactive/All`) applies to the full inventory list.
   - If category selected: show all articles in that category.
   - If no category selected: show all articles sorted by article number ascending.
7. Row columns (exact order):
   - `Article number`
   - `Article` (name/description)
   - `Supplier / Manufacturer`
   - `Batch` (if none, show `-`, but keep column visible)
   - `Quantity`
   - `Last activity` (date of latest issue OR receipt activity; date only)
8. Add row action `Edit article`:
   - Editable only descriptive fields (name, supplier/manufacturer, etc.)
   - Not editable here: quantity and batch.
9. Add row action `Inspect article`:
   - Show batches,
   - quantities per batch,
   - minimal stats: last issued date, last received date.
10. Add `Add article` action at bottom of inventory screen.
11. Remove standalone `Articles` screen; article create/edit flows should live under inventory (`Skladište`).

#### Technical Translation for Developers

1. Navigation and page copy:
   - Sidebar label `Skladište`.
   - Page title `Pregled artikala`.
2. Category model integration:
   - Replace current `is_paint` tab filter in inventory UI with category-driven filter control.
   - Canonicalize categories using existing `article_group` field with strict enum validation and controlled values (no new DB field required in this phase).
3. Inventory list data contract expansion:
   - Include/derive `supplier/manufacturer`, category, and last activity date in inventory listing DTO.
   - Keep batch column always present (`-` for non-batch items).
4. Sorting/filtering:
   - Default sort by numeric/article-no ascending when category filter is not active.
   - Category filter should be deterministic and stable.
   - Record-state filter must map to backend `is_active` states (`Active=true`, `Inactive=false`, `All`).
5. Article actions:
   - `Edit article` opens modal/drawer scoped to descriptive fields only.
   - `Inspect article` opens detail panel/modal with per-batch quantities and minimal activity stats.
6. Merge `Articles` module into `Skladište`:
   - Move/create article creation UI to inventory screen bottom section.
   - Remove separate `/articles` route and sidebar item (or keep hidden compatibility redirect during transition).

#### Conflict Check (Locked Rules / Existing Decisions)

- **Category shift implication**:
  - Current system uses `is_paint` heavily for UI and batch logic.
  - Category filter replacement is compatible for listing UX, but batch rules must remain bound to `has_batch` decision (not category itself).
- **Owner decision applied (supplier/manufacturer)**:
  - Use one unified field semantics in this phase (`supplier/manufacturer`) mapped to existing model field.
- **Owner decision applied (last activity)**:
  - Use `last_activity_date = max(last_consumption, last_receipt)` per article.
- **RBAC caution**:
  - `Edit article` and `Add article` remain ADMIN capabilities per locked RBAC table.
  - OPERATOR should keep read-only inventory view.

#### Backend Implementation Notes (Owner Decisions Applied)

1. **Category persistence model**:
   - Use `article_group` as controlled enum-like category code with validation against the approved category list.
2. **Supplier semantics**:
   - Keep single underlying model field and present as `Supplier / Manufacturer` in UI.
3. **Inventory listing contract**:
   - Extend endpoint(s) to provide category, supplier/manufacturer, and `last_activity_date` efficiently.
4. **Inspect article endpoint**:
   - Implement dedicated API for article inspection (batch breakdown + last issued/received + last activity) for predictable UI behavior.
5. **Articles screen decommission plan**:
   - Decide transition strategy for `/articles` features (aliases, archive/restore/delete) before route removal.

#### Suggested Acceptance Criteria (for future implementation task)

1. Sidebar/menu shows `Skladište`; page title shows `Pregled artikala`.
2. Record-state filter `Active / Inactive / All` exists and `Inactive` maps to archived behavior.
3. Category filter `Filtriraj kategorije` replaces paint/consumables tabs.
4. Category filtering and default article-number ascending order work as specified.
5. Inventory rows show columns in requested order with `Batch` fallback `-`.
6. `Edit article` exists and edits only descriptive metadata.
7. `Inspect article` shows batch quantities and minimal last issued/received statistics.
8. `Add article` is available on inventory screen.
9. Standalone `Articles` screen is removed from primary navigation.

---

### S-007: Articles Screen (`/articles`) Decommission

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Owner clarification**: Alias management will move to a new `Article Identifikator` module (ADMIN + OPERATOR), not to `Skladište`.
**Owner decision**: All remaining admin article-management functions must migrate into `Skladište` before `/articles` removal.

#### Requested Changes (MUST)

1. Remove standalone `Articles` screen from module/navigation.
2. Move needed features into `Skladište` screen:
   - `Active / Inactive / All` state filters (using `Inactive` label, not `Archived`).
   - `Add article` flow.
   - `Edit article` flow for descriptive metadata.
   - `Set Inactive` and `Reactivate` actions.
   - `Hard Delete` as admin maintenance action.
3. Keep ability to mark article inactive from `Skladište` (archive behavior via `is_active=false`).

#### Technical Translation for Developers

1. Frontend IA cleanup:
   - Remove `/articles` from sidebar primary navigation.
   - Route may temporarily redirect to `/inventory` during migration window.
2. Feature migration:
   - Port article state filtering and create action into `Skladište`.
   - Reuse existing archive/restore APIs, but expose user-facing label `Inactive`.
   - Port edit and hard-delete actions to `Skladište` admin actions menu.
3. Terminology alignment:
   - UI uses `Inactive`; backend may continue using `is_active` and archive endpoints.
4. Hard delete safeguards:
   - Keep backend reference checks (`ARTICLE_IN_USE`) as mandatory block.
   - Require explicit destructive confirmation in UI (typed confirm or double confirm) to avoid accidental removal.

#### Conflict Check (Locked Rules / Existing Decisions)

- **No locked-rule conflict**: this is IA consolidation and naming alignment.
- **RBAC alignment**: article management remains ADMIN-only.
- **Migration caution**:
  - removing `/articles` requires relocating remaining admin actions to avoid feature loss.
  - alias capabilities are explicitly moved to `Article Identifikator` module (shared ADMIN/OPERATOR), which requires RBAC/API adjustments because current alias endpoints are admin-scoped.

#### Backend Dependency / Decision Required

1. No mandatory schema change for active/inactive behavior (existing `is_active` already supports it).
2. Optional API cleanup after frontend migration:
   - Keep existing article endpoints; only route/view decommission is required.
3. New module dependency:
   - Define and implement `Article Identifikator` endpoints/permissions for alias search and "article not found" reporting workflow.
4. Owner decision applied:
   - `Create`, `Edit`, `Set Inactive/Reactivate`, `Active/Inactive/All`, and `Hard Delete` must all be available via `Skladište` admin workflows before `/articles` is removed.

#### Suggested Acceptance Criteria (for future implementation task)

1. `Articles` is no longer shown as standalone menu item.
2. `Skladište` provides `Active / Inactive / All` filtering.
3. `Add article` and `Edit article` are accessible from `Skladište` (ADMIN only).
4. Admin can set item to `Inactive` and reactivate it from `Skladište`.
5. Hard delete is available as admin maintenance action in `Skladište` and remains blocked when references exist.

---

### S-008: Batches Screen (`/batches`) Decommission

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Owner direction**: standalone `Batches` screen has no operational value; batch creation must happen through receiving flow (`Ulaz robe` under future `Narudžbe` module).

#### Requested Changes (MUST)

1. Remove standalone `Batches` screen from module/navigation.
2. Remove manual “New Batch” creation UX from dedicated screen.
3. Keep batch creation tied to receiving process:
   - batch is created/reused during `Ulaz robe` receipt entry.
4. Migrate useful batch-related visibility from `Batches` screen to relevant screens:
   - receiving context (`Ulaz robe`) and
   - article/inventory inspection context (`Skladište` -> `Inspect article`).

#### Existing Logic Found (to Preserve During Migration)

1. Frontend `/batches` currently provides:
   - Article selection + batch list by article.
   - Manual create batch (`POST /api/batches`) with expiry input.
   - Batch status and expiry visualization.
2. Backend batch APIs:
   - `GET /api/articles/<article_no>/batches` (active batches for article).
   - `POST /api/batches` (admin manual batch create).
3. Receiving service already supports target behavior:
   - On receive, batch is reused or auto-created if missing.
   - Expiry mismatch protection exists (`BATCH_EXPIRY_MISMATCH`).
   - Batch code validation and consumable/system-batch handling exist.

#### Technical Translation for Developers

1. Frontend IA cleanup:
   - Remove `Batches` sidebar item and `/batches` primary route exposure.
2. Receiving-first batch flow:
   - Keep all “new batch” entry only in `Ulaz robe`.
   - Reuse existing “existing/new batch” feedback currently present in receiving UI.
3. Visibility migration:
   - Move “list batches for selected article” capability into `Inspect article` details in `Skladište`.
   - Keep expiry/status indicators available in that inspect view.
4. API retention strategy:
   - Keep `GET /api/articles/<article_no>/batches` for draft/receiving/inspect lookups.
   - `POST /api/batches` can be hidden from UI first; later decide if endpoint remains for admin maintenance/API-only use.

#### Conflict Check (Locked Rules / Existing Decisions)

- **No locked-rule conflict**: moving batch creation under receiving aligns with existing decisions that receiving is the controlled inbound path.
- **Consistency gain**: removes parallel batch-creation path that bypasses receiving context/order linkage.
- **Operational caution**:
  - Some workflows still need batch lookup by article (draft entry, receiving validation, inspect views); keep lookup APIs.

#### Backend Implementation Notes (Owner Decision Applied)

1. Endpoint lifecycle for `POST /api/batches`:
   - **Owner decision**: deprecate endpoint after full migration and update clients/tests/docs.
   - Target model: batch creation allowed only through `Ulaz robe` receiving workflow.
2. Ensure receiving/inspect screens expose all needed batch data so removed screen does not reduce visibility.

#### Suggested Acceptance Criteria (for future implementation task)

1. `Batches` is no longer visible as standalone menu/module.
2. New batch creation is possible only through `Ulaz robe` receiving workflow.
3. Batch list/expiry visibility is available through `Skladište` inspect flow and receiving context.
4. Draft and receiving flows that depend on batch lookup continue to function unchanged.

---

### S-009: Reports Screen (`/reports`) Refactor to `Izvještaji`

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Owner direction**: transaction log table should not be primary content of reports; reports should become business-oriented module with inventories/surplus/statistics.  
**Owner clarifications recorded**:
- `Inventurna lista` must be rowed by `article + batch` (not article-only).
- Batch-aware quantity fields must exist per row; non-batch items still show batch fields with `-` for consistency.
- Reorder yellow zone is when current quantity is within `10%` above threshold.

#### Requested Changes (MUST)

1. Rename screen/module:
   - `Reports` -> `Izvještaji`.
2. Remove current "all transactions table" from primary Reports UI.
3. Reports module should contain these sub-screens:
   - `Inventurna lista`
   - `Surplus lista`
   - `Statistike`
4. `Inventurna lista` requirements:
   - list all articles with current state,
   - export to Excel and PDF,
   - columns: `article number`, `article description`, `article category`, `batch`, `trenutno stanje`, `novo stanje`.
   - rows are `article + batch`; each row has quantity for that batch.
   - for non-batch items, batch-related fields remain visible with `-`.
   - `novo stanje` entered during inventory count.
   - if `novo stanje < staro`: difference becomes inventory shortage draft for later approval.
   - if `novo stanje > staro`: difference goes to surplus list.
5. `Surplus lista` requirements:
   - show all articles with surplus,
   - export to Excel and PDF,
   - do not change existing surplus consumption logic (surplus-first behavior remains).
6. `Statistike` requirements:
   - add article search by article number,
   - show consumption charts for selected article (initial implementation allowed; detailed feedback later),
   - show `Top 20` consumers in current month (auto-updating from outbound flows),
   - show potential orders list based on reorder threshold with 3-level colors:
     - green: far above threshold (bottom),
     - yellow: quantity is within 10% above threshold,
     - red: below threshold (top, urgent).
   - these lists belong inside `Statistike` sub-screen.

#### Technical Translation for Developers

1. IA/UI structure:
   - Replace single transaction report table with tabbed/segmented reports workspace:
     - `Inventurna lista` | `Surplus lista` | `Statistike`.
2. Inventurna lista flow:
   - Build editable count grid by `article + batch` with current quantity + input for new quantity for each batch row.
   - Keep batch columns visible for all rows; use `-` where batch is not applicable.
   - Submit counts through existing inventory count service behavior (shortage draft vs surplus adjustment).
3. Export capabilities:
   - Provide Excel + PDF export actions for inventurna and surplus lists.
4. Surplus list:
   - Read-only display sourced from surplus/current inventory data.
5. Statistics initial version:
   - Per-article charts from transaction history.
   - Top 20 consumption list for current month (derived from consumption transactions).
   - Reorder-risk list from current stock vs `reorder_threshold`.
6. Transaction history placement:
   - Transaction audit can remain available via API/admin tools but should no longer dominate the business reports screen.

#### Conflict Check (Locked Rules / Existing Decisions)

- **RBAC alignment**: Reports remain ADMIN-only (LOCKED Rule 12).
- **Inventory count logic alignment**: Requested shortage/surplus behavior matches existing locked inventory count rules.
- **Surplus logic alignment**: Requested read-only surplus view with unchanged consumption behavior is aligned.
- **Granularity caution**:
  - Existing inventory model is batch-aware and owner chose article+batch rows, which avoids hidden per-batch allocation errors.
- **Transaction semantics caution**:
  - For "Top 20 consumers", consumption should be based on actual outflow transactions (`STOCK_CONSUMED` + `SURPLUS_CONSUMED`), not raw `WEIGH_IN` event alone.

#### Backend Implementation Notes (Owner Decisions Applied)

1. Inventura granularity:
   - **Owner decision**: use explicit `article + batch` rows.
   - Non-batch items keep batch columns visible with `-` placeholders.
2. Export implementation:
   - Decide server-side export endpoints vs client-side generation for Excel/PDF.
3. Statistics contract:
   - Implement all proposed baseline chart/list options in first iteration.
   - Do not split lists by UOM.
4. Reorder-risk thresholds:
   - **Owner decision**: yellow zone is `threshold < qty <= threshold * 1.10`.
   - Red zone: `qty <= threshold`.
   - Green zone: `qty > threshold * 1.10`.

#### Suggested Acceptance Criteria (for future implementation task)

1. Reports menu displays `Izvještaji` and opens sub-screens `Inventurna lista`, `Surplus lista`, `Statistike`.
2. Inventurna lista supports `article + batch` rows, current/new state entry per row, and export to Excel/PDF.
3. Inventory count submission from inventurna lista produces shortage draft or surplus update exactly per locked rules.
4. Surplus lista displays surplus items and supports Excel/PDF export.
5. Statistike screen shows article-search-driven charts, top 20 monthly consumers, and reorder-risk list with red/yellow/green priority using yellow=within 10% above threshold.

---

### S-006: Approvals Screen (`/drafts`)

**Feedback date**: 2026-02-12  
**Source**: Screenshot + business feedback from project owner  
**Operational intent**: Admin approves operator scale inputs as daily lists, not item-by-item.  
**Owner clarification**: Aggregation is allowed only for same `article + batch`; same article with different batch must remain separate row.

#### Requested Changes (MUST)

1. Keep screen ADMIN-only.
2. Replace current one-row-per-draft approval UX with day-based list UX:
   - Admin chooses date (e.g., `17.02.`) and sees all entries for that day.
3. Admin can edit quantities in the day list and approve/reject the whole list at once.
4. Row fields inside daily list:
   - `ID`:
     - Reserve logic for future scanner/scale-linked identity (hardware integration later).
   - `Created At`:
     - show time only (date already represented by selected list/day).
   - `Name / Items`:
     - show article code + article name (not auto-generated draft group name).
   - `Total Qty`:
     - show entered quantity.
     - if same article with same batch is entered multiple times in the day, aggregate into one row with summed quantity.
     - if same article appears in different batches, create separate rows (no cross-batch aggregation).
     - provide drill-down (`draft_group`) to inspect how many entries and at which times.
   - `Status`:
     - move to list-level (daily list status), not per row.
   - `Source`:
     - represent place/device of entry; prepare logic for future values `Vaga 1`, `Vaga 2`, etc.
   - `Actions`:
     - move to list-level: `Approve`, `Reject`, `Edit`.

#### Technical Translation for Developers

1. Data presentation model:
   - Introduce daily approval list view keyed by operational date.
   - Within each day, aggregate lines by `article + batch` for primary table display.
2. Detail/drill-down model:
   - Keep underlying raw draft entries accessible in detail panel to preserve traceability (times, per-entry quantities, source).
3. Approval workflow:
   - Execute approval/rejection at day-list level (single action for full list).
   - Retain atomic behavior to prevent partial approval corruption.
4. Quantity editing:
   - Support pre-approval edits in day-list workflow.
   - Ensure edits are persisted in underlying draft records before list-level approval.
5. Future hardware readiness:
   - Standardize source identity fields to support `Vaga N` and scanner-linked entry IDs later without redesign.
6. UI structure:
   - Top-level list by day + list-level status/actions.
   - Nested table/detail for aggregated article rows with expandable raw-entry history.

#### Conflict Check (Locked Rules / Existing Decisions)

- **No conflict with RBAC**: ADMIN-only approvals remain aligned with locked Rule 12.
- **No conflict with stock/surplus rules** if approval execution still uses existing surplus-first and stock integrity logic.
- **Audit caution (Rule 11)**:
  - Aggregated display is fine, but system must retain raw per-entry audit trail and source metadata.
- **Current architecture mismatch**:
  - Existing API groups by `draft_group` entities and currently many operator entries are auto-created as single-line groups.
  - Daily list aggregation and list-level status/actions require either:
    - new day-list abstraction/API, or
    - revised grouping strategy at draft creation time.

#### Backend Dependency / Decision Required

1. **Daily list entity strategy**:
   - Decide whether daily list is:
     - virtual aggregation query over existing drafts/groups (recommended first step), or
     - persisted entity with explicit lifecycle/status.
2. **Aggregation key** (owner decision applied):
   - Group only by `article + batch`.
   - Same article across different batches must stay as separate rows.
3. **Edit propagation rule** (owner decision applied):
   - Pre-approval edits overwrite pending draft values.
   - No correction transaction is created before approval because inventory is unchanged until approval.
4. **List status model**:
   - Define day-list statuses (`DRAFT/PENDING/APPROVED/REJECTED`) and mapping from underlying draft statuses.
5. **Source/device model** (owner decision applied):
   - Standardize canonical fields now: `scale_id`, `scanner_id`, `station_id`, `source_label`, optional hardware metadata map.
6. **Day-boundary rule** (owner decision applied):
   - Persist timestamps in UTC.
   - Group/label operational day in `Europe/Berlin` timezone (Hamburg), with future location-based timezone extensibility.

#### Suggested Acceptance Criteria (for future implementation task)

1. Approvals page shows daily lists and allows selecting a specific day.
2. Within selected day, repeated entries are aggregated only when `article + batch` are identical; different batch stays separate row (with expandable raw-entry detail).
3. Admin can edit quantities before approval at list workflow level.
4. Admin can approve/reject entire daily list in one action.
5. List-level status and actions are visible; row-level status/actions are removed from primary table.
6. Created time is shown as time-only within day view.
7. Source model is ready to show `Vaga N` identifiers when hardware is introduced.

---

### S-010: Orders Module (`/orders`) - New Module

**Feedback date**: 2026-02-17  
**Source**: Business workflow feedback from project owner  
**Owner decisions recorded**: Yes (scope, lifecycle, receiving linkage, numbering, RBAC)

#### Requested Changes (MUST)

1. Add new parent module `Narudžbe` with 3 sub-screens:
   - `Otvorene narudžbe`
   - `Ulaz robe` (existing receiving screen, moved under Orders IA)
   - `Zatvorene narudžbe`
2. Order creation (`ADMIN only`) must support:
   - `order_number` (auto-generated if empty, or manual SAP number input),
   - `supplier_code`,
   - `supplier/manufacturer` name.
3. Add per-line `delivery_date` field (entered when supplier confirms date).
4. Order lines are created by article number and saved as list lines under order.
5. Partial receiving is supported:
   - one order can be received over multiple delivery notes,
   - one delivery note can contain items from multiple orders.
6. Every receiving line must capture:
   - `order_line_id` (when linked to order),
   - `delivery_note_number`.
7. Order closes automatically when all lines are fully received.
8. If some lines are never delivered:
   - admin can edit order and remove disputed lines,
   - order then auto-closes when remaining lines are fully received.
9. Over-receipt handling:
   - no special over-receipt logic required,
   - admin resolves by editing order quantities/lines.
10. Receiving without order must be allowed:
   - ad-hoc receive flow is valid,
   - details must be written in `note`.
11. Unit semantics for Orders/Receiving must be fully unit-aware (not KG-only).

#### Technical Translation for Developers

1. New domain model is required (existing `transactions.order_number` is not enough):
   - `suppliers` (or equivalent): `supplier_code` (unique), `name` (supplier/manufacturer).
   - `orders` (header): `order_number` (unique), supplier reference, status, timestamps.
   - `order_lines`: article, ordered quantity, UOM, `delivery_date`, received quantity, status.
2. Receiving integration:
   - Extend receive contract to accept `delivery_note_number` and optional `order_line_id`.
   - If `order_line_id` is present:
     - validate line exists, belongs to open order, article matches,
     - update line received quantity.
   - If no `order_line_id`:
     - process as ad-hoc receiving,
     - require meaningful `note`.
3. Transaction/audit linkage:
   - persist `delivery_note_number` and `order_line_id` on transaction (or equivalent normalized relation) for traceability.
4. Order numbering rules:
   - auto-generated numbers must be globally unique,
   - auto-generated format is `ORD-xxxx` (numeric padded),
   - manual numbers must be uniqueness-validated and return conflict if duplicate.
5. Open/Closed routing logic:
   - `Otvorene narudžbe`: status not fully received.
   - `Zatvorene narudžbe`: all active lines fully received.
6. Edit semantics:
   - line delete/quantity edit must re-evaluate order status immediately.
7. Operator visibility (limited):
   - keep order management ADMIN-only,
   - future OPERATOR visibility limited to delivery date info for a specific article (read-only surface only).

#### Conflict Check (Locked Rules / Existing Decisions)

- **RBAC alignment**:
  - ADMIN-only create/edit/close orders is aligned with locked role policy.
  - OPERATOR access must remain read-only and minimal.
- **Current API contract impact**:
  - existing receive schema requires `order_number`; allowing ad-hoc receiving requires contract change.
- **Audit alignment (Rule 11)**:
  - each receive action must still create transaction with complete linkage metadata.
- **Multi-unit impact (G-003)**:
  - Orders + Receiving must follow unit-aware refactor; cannot stay `quantity_kg` only.

#### Backend Dependency / Implementation Notes

1. Add new endpoints for Orders:
   - create/list/get/update,
   - list open/closed,
   - line-level operations.
2. Extend receiving endpoint/service:
   - support `order_line_id` + `delivery_note_number`,
   - support ad-hoc (no order) receive path.
3. Add indexes:
   - unique `orders.order_number`,
   - unique `suppliers.supplier_code`,
   - indexed `transactions.delivery_note_number`,
   - indexed `transactions.order_line_id`.
4. Preserve backward compatibility:
   - existing `order_number` field remains usable in reporting/history during migration.

#### Suggested Acceptance Criteria (for future implementation task)

1. `Narudžbe` module exists with sub-screens `Otvorene narudžbe`, `Ulaz robe`, `Zatvorene narudžbe`.
2. ADMIN can create order with auto or manual order number; duplicate number returns conflict error.
3. Supplier code + supplier/manufacturer are persisted and visible on order header.
4. Every order line supports article + quantity + UOM + delivery date.
5. Receiving with `order_line_id` updates linked line; receiving without order is still possible with note.
6. `delivery_note_number` is stored for each receiving transaction.
7. Order auto-moves from open to closed when all active lines are fully received.
8. Editing/removing unresolved lines can close order as specified by owner workflow.

---

### S-011: Article Identifikator Module (`/article-identifikator`) - New Module

**Feedback date**: 2026-02-17  
**Source**: Business workflow feedback from project owner  
**Owner decisions recorded**: Yes (dual-role usage, alias lookup flow, missing-article reporting)

#### Requested Changes (MUST)

1. Add new module `Article Identifikator` used by both OPERATOR and ADMIN.
2. Primary workflow:
   - operator enters what they see on work card (name/code/alias),
   - system resolves and returns canonical article from warehouse system.
3. If no match is found:
   - operator can submit report for "non-existing article".
4. Missing-article reports list must exist and include:
   - report ID,
   - reporter identity (user ID),
   - entered description/code text from operator.
5. Module roles:
   - OPERATOR: lookup + submit report,
   - ADMIN: lookup + review/process reported items.

#### Technical Translation for Developers

1. Split capabilities into two concerns:
   - alias/article resolution (search),
   - missing-article reporting queue.
2. New reporting entity is required (example: `missing_article_reports`) with fields:
   - `id`,
   - `reported_by_user_id`,
   - `raw_input`,
   - `normalized_input`,
   - `status` (e.g., `OPEN`, `IN_REVIEW`, `RESOLVED`, `CLOSED`, `REJECTED`),
   - `resolved_article_id` (nullable),
   - `admin_note` (nullable),
   - `created_at`, `resolved_at`, `resolved_by_user_id`.
3. API contract changes:
   - current `/api/articles/resolve` is ADMIN-only today; extend or add new endpoint to allow OPERATOR lookup safely.
   - add endpoint for report submit (OPERATOR + ADMIN).
   - add endpoint/list for admin queue review and status updates.
   - host queue/list UI under `Izvještaji` as dedicated identifier-query sub-view.
4. Alias constraints remain unchanged:
   - alias remains lookup-only,
   - global uniqueness and alias limits stay enforced by existing rules.
5. UX expectations:
   - fast single-input lookup with exact + normalized matching,
   - clear "not found" state with immediate `Prijavi nepostojeci artikl` action,
   - admin queue table with filters by status/date/reporter.

#### Conflict Check (Locked Rules / Existing Decisions)

- **RBAC alignment**:
  - No conflict with admin-only article management as long as OPERATOR cannot create/edit aliases directly.
  - OPERATOR scope is lookup + report submit only.
- **LOCKED alias rule alignment (Rule 5)**:
  - New module must not violate alias uniqueness/limit semantics.
- **Audit/data safety**:
  - Reporting workflow is non-transactional for stock and does not affect inventory balances.

#### Backend Dependency / Implementation Notes

1. Add missing-article report model + migration.
2. Add endpoints:
   - resolve (role-expanded or dedicated public-for-auth users),
   - create report,
   - admin report queue list/update.
3. Add indexes for queue performance:
   - `status`,
   - `created_at`,
   - `reported_by_user_id`,
   - normalized input for dedup/search.
4. Dedup logic (owner decision applied):
   - merge repeated reports with same normalized input into single active item.

#### Suggested Acceptance Criteria (for future implementation task)

1. OPERATOR and ADMIN can open `Article Identifikator` and search by alias/text/code.
2. Successful lookup returns canonical article data from system.
3. Not-found state provides report action and creates a missing-article report record.
4. Report list shows ID, reporter user ID, entered description/code, status, and timestamp.
5. ADMIN can process report queue and mark reports as resolved/rejected with note.
6. Report is considered closed only via explicit admin close action.
