# Task Brief: TASK-0026 — Frontend v3 Phase 1 (Shell, i18n, Layout Foundation)

**Created**: 2026-02-17  
**Assigned to**: Frontend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Build global frontend foundations for v3: Croatian-first i18n with language switcher, standardized layout tokens, and baseline navigation structure for upcoming module refactors.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
3. `docs/team/RULES_OF_ENGAGEMENT.md`
4. `docs/team/DECISIONS.md`
5. `docs/team/AGENT_INSTRUCTIONS.md`

---

## Scope

### In Scope

- Implement i18n scaffolding with locales: `hr`, `en`, `de`, `hu`.
- Set Croatian as baseline/default UI language.
- Add language switcher in app shell.
- Apply approved Croatian terms:
  - `Skladišni Menadžer`
  - `Odspojen`
  - `Pretraži po imenu/kodu/alijasu`
- Introduce global layout tokens (content widths, gutters, breakpoints).
- Reduce side gutters and widen content area for all screens.
- Tablet-aware shell behavior: tablet profile centered on `Automatski unos` workflow.

### Out of Scope

- Orders and receiving screen implementation (Phase 2).
- Approvals and outbound refactor (Phase 3).
- Inventory/reports/module rewrites (Phase 4).

---

## Technical Changes

### 1) i18n Architecture

- Integrate localization framework for runtime language switching.
- Move hardcoded UI strings into translation keys.
- Ensure full Croatian diacritics in HR translations (`č`, `ć`, `ž`, `š`, `đ`, `dž`).

### 2) App Shell & Navigation Foundation

- Add language selector in top app shell.
- Prepare nav structure to support upcoming module IA changes without yet shipping all new screens.

### 3) Layout Tokens

- Create shared spacing/width tokens for forms and tables.
- Widen central content region and reduce left/right dead space.
- Ensure long article names are readable in expected table/form layouts.

### 4) Tablet Baseline

- Define responsive breakpoints for tablet and desktop.
- Ensure tablet default usage path favors `Automatski unos` access.

---

## Acceptance Criteria

1. [ ] App supports `hr/en/de/hu` language switching.
2. [ ] Default language is Croatian with correct diacritics.
3. [ ] Approved HR terms are visible in UI via i18n keys.
4. [ ] Global content area is visibly wider with consistent layout tokens.
5. [ ] Frontend build passes with no i18n runtime errors.

---

## Test Plan

### Automated

```bash
cd desktop-ui
npm run build
```

### Manual

1. Toggle language between all 4 locales and verify UI updates.
2. Verify Croatian terms render with correct diacritics.
3. Validate widened layouts on main screens.
4. Validate tablet breakpoint behavior in responsive mode.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`
- [ ] `docs/tasks/TASK-0021-v3-implementation-master-plan.md` (status line)

---

## Status Updates

- 2026-02-17: Task created.

