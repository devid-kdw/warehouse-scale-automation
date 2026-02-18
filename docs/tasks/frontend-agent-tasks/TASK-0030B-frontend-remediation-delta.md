# Task Brief: TASK-0030B — Frontend Remediation Delta (Post-Audit)

**Created**: 2026-02-18  
**Assigned to**: Frontend Agent (remediation delta)  
**Status**: Ready  
**Priority**: P0

---

## Goal

Zatvoriti preostale gapove nakon TASK-0030 implementacije.  
Build prolazi, ali runtime/contract i UX nisu u potpunosti usklađeni.

---

## Context

Orchestrator audit nakon frontend isporuke potvrdio je da su ostali otvoreni:
- P0 contract mismatch-evi (`orders`, `daily approvals`),
- RBAC nedosljednost (`/izlaz`),
- nedovršeni Orders/Inventory flowovi,
- djelomična i18n i type cleanup nedovršenost.

---

## P0 (Blockers)

1. **Orders API routes**
- U `desktop-ui/src/api/orders.ts` prebaciti sve rute na `/api/orders/*`.
- Trenutni `/orders/*` pozivi su neispravni za backend.

2. **Daily Approvals contract alignment**
- U `desktop-ui/src/pages/Drafts/DraftApproval.tsx`:
  - summary koristi `total_lines` i `total_qty` (ne `draft_count`, `status`),
  - detail tretirati kao listu (ne `detailData.groups`),
  - koristiti `total_qty` i `draft_ids` iz response-a.
- Uskladiti render i edit tok s backend shemom.

3. **RBAC consistency for `/izlaz`**
- Sidebar i route guard moraju biti konzistentni.
- Nema linka prema ruti koju trenutna rola ne smije otvoriti.
- Primijeni isti policy kao u `RULES_OF_ENGAGEMENT.md` + `DECISIONS.md` (ako konflikt, prijavi blocker).

---

## P1 (High)

1. **Orders UX completion**
- `CreateOrder` mora omogućiti unos line stavki pri kreiranju (article, qty, uom, delivery_date, note).
- `OrderDetail` mora omogućiti line upsert/edit flow (ne samo header edit + remove).

2. **Inventory parity completion**
- U `desktop-ui/src/pages/Inventory.tsx`:
  - zamijeniti `Paint/Consumables` s category filterom prema odobrenom skupu,
  - implementirati `Active / Inactive / All` filter (state).

3. **Identifikator status handling**
- U `desktop-ui/src/pages/Identifikator/AdminQueue.tsx`:
  - podržati backend status `OPEN` u prikazu i workflow-u.
- Ne smije se izgubiti mogućnost obrade novog reporta zbog status mapping-a.

4. **Reports top-consumers response shape**
- U `desktop-ui/src/pages/Reports/Statistike.tsx`:
  - `top-consumers` endpoint vraća listu direktno, ne `{ items: [...] }`.
- Uskladiti parsiranje bez rušenja UI-a.

---

## P2 (Polish / Completion)

1. **i18n completion**
- Ukloniti preostale hardcoded EN stringove s glavnih ekrana/komponenti.
- Posebno: `Login`, common state komponente, preostale Orders/Inventory helper poruke.

2. **Type/model cleanup**
- U `desktop-ui/src/api/types.ts` i povezanim komponentama:
  - ukloniti nepotrebne legacy `quantity_kg` / `total_quantity_kg` reference gdje canonical polja već postoje.
- Ostaviti legacy samo ako je nužan fallback i jasno komentiran.

---

## Canonical Contract Reminder

- Orders: `/api/orders*`
- Daily approvals: `/api/drafts/daily*`
- Identifikator admin: `/api/admin/identifikator/queue*`
- Article patch: `/api/articles/id/<id>`
- Reports stats: `top-consumers` vraća listu (`many=True`)

---

## Acceptance Criteria

1. [ ] Orders API pozivi rade preko `/api/orders/*`.
2. [ ] Daily approvals ekran koristi točan summary/detail payload shape.
3. [ ] `/izlaz` RBAC je konzistentan između sidebara i route guardova.
4. [ ] Orders create/detail podržavaju line-level create/edit tok.
5. [ ] Inventory ima category + active/inactive/all filtere.
6. [ ] Admin queue obrađuje i `OPEN` reporte bez rupe u workflowu.
7. [ ] `Statistike` ispravno prikazuju top-consumers bez shape mismatch-a.
8. [ ] Preostali hardcoded EN stringovi uklonjeni iz glavnih flowova.
9. [ ] `npx tsc && npx vite build` prolazi.

---

## Verification

### Automated

```bash
cd desktop-ui
npx tsc
npx vite build
```

### Manual

1. Orders: create s lineovima, detail edit lineova, remove line.
2. Approvals: daily list + detail + edit qty + approve/reject.
3. RBAC: `/izlaz` vidljiv/sakriven i dostupan prema istoj roli.
4. Inventory: category filter + state filter.
5. Identifikator admin queue: novi report (`OPEN`) -> obrada.
6. Reports stats: top-consumers lista se renderira bez greške.

---

## Required Output

- Summary po P0/P1/P2.
- Popis fileova.
- API contract alignment napomene.
- Build + manual test evidence.
- Preostali rizici (ako ih ima).

