# Warehouse Scale Automation - Project Knowledge

**Version**: 2.0 (planning alignment wave)  
**Last Updated**: 2026-02-17

This file summarizes current business direction and architectural intent.  
If conflicts exist, precedence is:
1. `docs/team/RULES_OF_ENGAGEMENT.md`
2. `docs/team/DECISIONS.md`
3. Active task brief (`docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`)

---

## 1. Business Purpose

Warehouse operations platform for controlled inventory intake/outflow with full auditability.

Primary business goals:
- reliable stock control,
- approval-controlled consumption,
- batch/expiry safety,
- practical operator workflows,
- managerial visibility (inventura, surplus, statistics, order planning).

---

## 2. Roles

### ADMIN
- manage article master data,
- process approvals,
- receive stock,
- manage orders,
- view reports,
- process missing-article reports.

### OPERATOR
- create drafts,
- view inventory,
- use Article Identifikator lookup,
- submit missing-article reports.

---

## 3. Locked Operational Invariants

- surplus-first consumption,
- stock never negative,
- audit transaction for every inventory-changing action,
- location fixed to 13 in v1,
- receiving remains admin-controlled.

---

## 4. Quantity Semantics Direction

Project is moving from KG-only semantics to unit-aware semantics.

Implications:
- article UOM is authoritative,
- UI labels and workflows must not assume only kg,
- migration must preserve historical `quantity_kg` audit data.

Current backend runtime boundary (post v3 backend wave):
- Canonical new-write direction is `quantity + uom`.
- Stock-changing conversions currently support `KG` and `L`.
- Some read contracts still expose legacy KG fields during transition.
- Full `quantity_kg` decommission is tracked as dedicated backend follow-up task (`TASK-0026A`).

---

## 5. Article and Batch Semantics

### Article
Core concept remains `article_no` + description, with descriptive metadata and status (`is_active`).

### Alias
Aliases are lookup-only shortcuts and remain globally unique.

### Batch
Batch requirement is governed by article batch-tracking capability (`has_batch` / `is_batch_tracked`), not by paint classification alone.

`is_paint` may remain as classification/category signal, but not as mandatory batch rule trigger.

---

## 6. Module Direction (UI/IA)

### Draft Entry
- operator-oriented automatic entry flow,
- simplified UI,
- no unnecessary admin/bulk elements.

### Izlaz (formerly Bulk Entry)
- outbound list workflow,
- system-assigned outbound reference,
- row behavior aligned with batch-tracking + unit-aware model.

### Narudzbe (new parent module)
Sub-screens:
- `Otvorene narudzbe`
- `Ulaz robe`
- `Zatvorene narudzbe`

Orders require header/line model and partial receipt lifecycle.

### Ulaz robe
- embedded receipt history,
- supports linked receiving (`order_line_id`) and ad-hoc receiving (note required).

### Skladiste
- consolidated inventory and article management surface,
- category filtering,
- active/inactive/all filtering,
- inspect/edit/add article workflows (ADMIN-controlled actions).

### Approvals
- daily-list oriented approval workflow direction,
- aggregation rule: same `article + batch` only.

### Izvjestaji
Business-oriented reports:
- inventurna lista,
- surplus lista,
- statistike.

### Article Identifikator (new)
- lookup by alias/text/code for ADMIN + OPERATOR,
- missing-article report submission,
- admin processing queue.

---

## 7. Orders Domain Direction

Approved model direction:
- `Order` + `OrderLine` entities,
- auto or manual `order_number` (unique),
- supplier code + supplier/manufacturer binding,
- per-line `delivery_date`,
- `delivery_note_number` captured on receiving,
- one delivery note can cover multiple orders,
- close order when all active lines fulfilled.

---

## 8. Reporting Direction

Reports are no longer transaction-table-first UX.

Required business views:
- inventory count list by `article + batch`,
- surplus overview,
- statistics (usage trends, top consumers, reorder risk tiers).

Yellow reorder zone rule: within 10% above threshold.

---

## 9. Hardware Roadmap

Scale/barcode integrations remain future phase, but data model should remain integration-ready (source/identity metadata).

---

## 10. Documentation Policy

- Old task briefs and status reports are historical snapshots.
- Current planning baseline is `TASK-0020`.
- Any rule/decision drift must be resolved before implementation starts.
- Backend contract snapshot reference: `docs/status/ORCHESTRATOR_BACKEND_AUDIT_2026-02-17.md`.
