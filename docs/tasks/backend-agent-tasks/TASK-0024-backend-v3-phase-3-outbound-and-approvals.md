# Task Brief: TASK-0024 — Backend v3 Phase 3 (Outbound & Approvals)

**Created**: 2026-02-17  
**Assigned to**: Backend Agent  
**Status**: Planning  
**Priority**: P0

---

## Goal

Refactor outbound draft grouping and approvals workflow to daily list-based processing, while preserving stock integrity and audit guarantees.

---

## Mandatory Reading Before Coding

1. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
2. `docs/tasks/backend-agent-tasks/TASK-0022-backend-v3-phase-1-foundation-and-migrations.md`
3. `docs/tasks/backend-agent-tasks/TASK-0023-backend-v3-phase-2-orders-and-receiving.md`
4. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md` (`S-001`, `S-002`, `S-006`)
5. `docs/team/RULES_OF_ENGAGEMENT.md` (Rules 1, 3, 8, 13, 14, 17, 18)

---

## Scope

### In Scope

- Outbound grouping model updates (`Izlaz` semantics):
  - system-assigned outbound number (`Broj izlaza`),
  - group-level description/comment.
- Approvals daily aggregation:
  - group by operational day (`Europe/Berlin`),
  - aggregate only same `article + batch`,
  - separate row for same article with different batch.
- Pre-approval edit behavior:
  - edits overwrite pending values,
  - no correction transaction before approval.
- List-level actions for daily approval queue:
  - approve list,
  - reject list,
  - edit list entries.
- Source identity persistence (`scale_id`, `scanner_id`, `station_id`, `source_label`).

### Out of Scope

- Orders receive logic (Phase 2).
- Reports and identifier queues (Phase 4).

---

## Technical Changes

### 1) Outbound Group Metadata

- Add outbound numbering field with deterministic sequence.
- Add group-level description field and API exposure.

### 2) Daily Aggregation Endpoints

- New/updated endpoints for:
  - day list retrieval,
  - day detail retrieval,
  - list-level approve/reject.
- Date grouping must be computed using `Europe/Berlin` while storing timestamps in UTC.

### 3) Edit Semantics Before Approval

- Update pending records directly when admin edits aggregate values.
- Ensure stock not updated until approval transaction occurs.
- Keep audit trail for final approved stock-impacting action.

### 4) Aggregation Rules

- Merge only rows with same `article_id + batch_id` (or equivalent batch key).
- Keep separate rows when batch differs.

---

## Acceptance Criteria

1. [ ] Outbound groups have system-generated `Broj izlaza` and group description.
2. [ ] Approvals can be listed by operational day in `Europe/Berlin`.
3. [ ] Aggregation merges only same article+batch entries.
4. [ ] Admin can edit pending aggregate values before approval without creating correction tx.
5. [ ] Day-level approve/reject actions work and update statuses correctly.
6. [ ] Source identity fields are persisted and available in API responses.

---

## Test Plan

### Automated

```bash
cd backend
pytest -v
```

### Focused

```bash
pytest tests/test_draft_groups.py -v
pytest tests/test_approvals.py -v
pytest tests/test_transactions.py -v
```

### Manual Contract Checks

1. Multiple same-day entries same article+batch -> one aggregate row.
2. Multiple same-day entries same article different batch -> separate rows.
3. Edit aggregate quantity before approval -> final approved stock reflects edited value.
4. Verify grouping date behavior around UTC boundary (Berlin day correctness).

---

## Rollout / Migration Notes

- Keep old approvals list API available temporarily if frontend not yet migrated.
- Add clear deprecation notice and target removal in Phase 4.

---

## Documentation Updates Required

- [ ] `docs/team/CHANGELOG.md`
- [ ] OpenAPI docs for new approvals endpoints

---

## Status Updates

- 2026-02-17: Task created.

