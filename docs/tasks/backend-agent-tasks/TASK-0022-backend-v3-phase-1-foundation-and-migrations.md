# Task Brief: TASK-0022 — Backend v3 Phase 1 (Foundation & Migrations)

**Created**: 2026-02-17  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Establish backend schema and contract foundations required for all v3 modules without breaking current runtime behavior.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
3. `docs/team/RULES_OF_ENGAGEMENT.md`
4. `docs/team/DECISIONS.md`
5. `docs/team/MIGRATIONS.md`
6. `docs/team/CHANGELOG.md`

---

## Scope

### In Scope

- Additive migration strategy for unit-aware direction and article metadata refactor.
- Article model updates for:
  - `has_batch` semantics,
  - category normalization key,
  - supplier label alignment (`supplier/manufacturer`),
  - `supplier_code` support.
- UOM catalog persistence model (open-entry + persistent catalog behavior).
- Canonical source identity fields preparation for future hardware integration.
- Compatibility layer so existing endpoints still function during phased rollout.

### Out of Scope

- Orders endpoints (Phase 2).
- Approvals aggregation behavior (Phase 3).
- Reports/Identifier endpoints (Phase 4).

---

## Technical Changes

### 1) Article and UOM Foundation

- Extend article schema/model to support v3 requirements:
  - batch-tracking boolean (`has_batch` or equivalent canonical field),
  - normalized category key,
  - supplier code,
  - supplier/manufacturer naming compatibility.
- Create UOM catalog entity with unique normalized key.
- Implement service behavior:
  - if incoming UOM exists -> reuse,
  - if incoming UOM is new -> persist into catalog.

### 2) Unit-Aware Transition Layer

- Add transitional quantity fields needed for future full cutover.
- Keep legacy `quantity_kg` compatible reads/writes where still required.
- Document mapping strategy to avoid audit/history loss.

### 3) Hardware Identity Canonical Fields (Preparation)

- Add canonical metadata fields for source identity where draft/ingest models require them:
  - `scale_id`
  - `scanner_id`
  - `station_id`
  - `source_label`
  - optional flexible metadata (`JSON`/dict)

### 4) Migration and Backfill

- Create migration(s) with deterministic backfill:
  - map existing paint-coupled behavior into new `has_batch` baseline.
  - initialize normalized category defaults for existing records.
- Update migration log and include rollback notes.

---

## Acceptance Criteria

1. [ ] New schema fields and tables are created with backward-compatible behavior.
2. [ ] Existing core flows still pass tests after migration.
3. [ ] UOM open-entry persistence works (new UOM stored and reusable).
4. [ ] `has_batch` field exists and is used as canonical batch-rule driver for new work.
5. [ ] Hardware identity fields are available in schema/model contracts.
6. [ ] `docs/team/MIGRATIONS.md` and `docs/team/CHANGELOG.md` are updated.

---

## Test Plan

### Automated

```bash
cd backend
pytest -v
```

### Focused

```bash
pytest tests/test_articles.py -v
pytest tests/test_inventory.py -v
pytest tests/test_drafts.py -v
```

### Manual Contract Checks

1. Create/update article with category, supplier/supplier_code, `has_batch`, UOM.
2. Submit payload with unseen UOM and verify catalog persistence.
3. Verify legacy endpoints still serialize expected fields.

---

## Rollout / Migration Notes

- Use additive migrations first, no destructive drops in Phase 1.
- Any renaming should expose API aliases to avoid immediate frontend breakage.
- Keep old fields available until Phase 4 decommission task.

---

## Documentation Updates Required

- [ ] `docs/team/MIGRATIONS.md`
- [ ] `docs/team/CHANGELOG.md`
- [ ] `docs/tasks/TASK-0021-v3-implementation-master-plan.md` (status line)

---

## Status Updates

- 2026-02-17: Task created.

