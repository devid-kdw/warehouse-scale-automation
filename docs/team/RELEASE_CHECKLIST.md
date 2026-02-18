# Release Checklist

Use this checklist before every release.

---

## 1. Backend Quality

- [ ] `pytest` passes.
- [ ] Migrations apply cleanly (`flask db upgrade`).
- [ ] Backend starts without errors.
- [ ] OpenAPI/Swagger reflects real contracts.

## 2. Frontend Quality

- [ ] `npm run build` passes.
- [ ] No runtime console errors in smoke flows.
- [ ] RBAC UI behavior verified for ADMIN and OPERATOR.

## 3. Documentation

- [ ] `docs/team/CHANGELOG.md` updated.
- [ ] `docs/team/MIGRATIONS.md` updated (if migration added).
- [ ] `docs/team/DECISIONS.md` updated (if policy changed).
- [ ] `docs/team/RULES_OF_ENGAGEMENT.md` updated only when explicitly approved.

## 4. Smoke Test (Manual)

### Authentication
- [ ] Login/logout works.
- [ ] Role rendering is correct in UI.

### Draft Flow
- [ ] OPERATOR can create draft.
- [ ] ADMIN can approve/reject.

### Inventory (`Skladiste`)
- [ ] Inventory list loads.
- [ ] Filters/search/actions behave per role.

### Orders (`Narudzbe`)
- [ ] Open/closed lists render.
- [ ] `Ulaz robe` receiving flow works.
- [ ] Partial receipts and status transitions work.

### Receiving (`Ulaz robe`)
- [ ] Linked receiving with `order_line_id` works (when in scope).
- [ ] Ad-hoc receiving without order works with note.
- [ ] `delivery_note_number` captured.

### Reports (`Izvjestaji`)
- [ ] ADMIN-only access enforced.
- [ ] Inventura / surplus / statistics views load.

### Article Identifikator
- [ ] Lookup works for ADMIN and OPERATOR.
- [ ] Not-found report submit works.
- [ ] Admin queue is visible/processable.

## 5. Post-Release Monitoring

- [ ] No critical backend errors in logs.
- [ ] No failed migration/data integrity incidents.
- [ ] No RBAC regressions reported by users.

---

Last Updated: 2026-02-17
