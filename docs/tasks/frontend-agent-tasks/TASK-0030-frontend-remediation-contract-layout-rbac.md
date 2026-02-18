# Task Brief: TASK-0030 — Frontend Remediation (Contract, Layout, RBAC, i18n)

**Created**: 2026-02-17  
**Assigned to**: Frontend Agent (new)  
**Status**: Ready  
**Priority**: P0 (production blocker)

---

## Cilj

Stabilizirati i dovršiti frontend implementaciju prema stvarno implementiranom backendu i zaključanim pravilima.

Ovaj task je remediation val nakon audita i uključuje:
- kritične API mismatch-eve,
- layout bug gdje content ulazi ispod sidebara,
- RBAC/UI nedosljednosti,
- nedovršenu hrvatsku lokalizaciju,
- nedovršene module (Orders, Approvals, Inventory, Reports, Identifikator).

---

## Kontekst (obavezno)

Audit je potvrdio da frontend build prolazi, ali runtime ugovori i UX nisu usklađeni.  
Korisnički feedback (screenshot): sadržaj je raširen i prekriva ga side menu. To je **hitni blocker**.

---

## P0 Blockeri (moraju biti riješeni prvi)

1. **Layout/AppShell overlap fix (screenshot blocker)**
- Popraviti glavni layout tako da content nikad ne ulazi ispod sidebara.
- Ukloniti/izmijeniti CSS override koji ruši Mantine AppShell offset (`.mantine-AppShell-main` override u `layout.css`).
- Ostaviti "wider content" cilj, ali unutar AppShell pravila (sidebar width + responsive offset).
- Verificirati desktop breakpoints i da naslovi/tablice/forme nisu odrezani lijevo.

2. **Orders API path fix**
- `desktop-ui/src/api/orders.ts` mora koristiti `/api/orders/*` (ne `/orders/*`).

3. **Identifikator contract fix (path + payload + method)**
- Endpoint namespace: `/api/identifikator/*` i admin `/api/admin/identifikator/*`.
- Lookup query param mora biti `query`.
- Missing report payload mora biti `{ raw_input, location_id }`.
- Admin update mora biti `PATCH /api/admin/identifikator/queue/<id>`.

4. **Daily approvals contract fix**
- Lista dana: koristiti `total_lines`, `total_qty`.
- Detail endpoint response tretirati kao listu (ne `{ groups: ... }`).
- PATCH payload za edit line: `{ article_id, batch_id, new_total_qty }`.

5. **Receipt history field fix**
- UI čitati `line.quantity` (ne `quantity_kg`) za receiving history.

6. **Article update endpoint fix**
- PATCH mora ići na `/api/articles/id/<id>`.

---

## P1 Visoki prioritet (odmah nakon P0)

1. **RBAC i navigation usklađenje**
- Ukloniti `/articles` iz sidebara (legacy screen decommission).
- Uskladiti `/izlaz` link i route guard:
  - ili ADMIN-only i link ADMIN-only,
  - ili OPERATOR+ADMIN i route `RequireAuth`.
- Ne smije postojati link koji vodi u zabranjeni ekran za trenutnu rolu.

2. **Orders UX completion**
- `CreateOrder` mora podržati stvarni unos line stavki (article, qty, uom, delivery_date, note), ne samo prazni `lines: []`.
- `OrderDetail` treba imati potpuni edit/upsert line flow prema backend ugovoru.

3. **Reports contract alignment**
- `Statistike` uskladiti s backend response shapeom:
  - consumption: `items[]`,
  - top-consumers: zaseban endpoint/list,
  - reorder-risk: `stock`, `threshold`, `risk_level`.
- `Surplus` koristiti canonical polja (`quantity`, `uom`) umjesto legacy pretpostavki.

4. **Export auth-safe implementation**
- Umjesto `window.open` na protected endpoint, koristiti authenticated blob download preko `apiClient` (Bearer token), pa `URL.createObjectURL`.

5. **Inventory parity (Phase 4 zahtjevi)**
- Zamijeniti trenutne `Paint/Consumables` tabove s filtriranjem po odobrenim kategorijama.
- Implementirati `Active / Inactive / All` filter na Inventory.

---

## P2 Završno usklađenje

1. **Hrvatska lokalizacija 100%**
- Ukloniti hardcoded EN stringove iz glavnih ekrana (`Login`, `Inventory`, `Orders`, `Reports`, `Identifikator`, `Approvals`, helper komponente).
- Sve UI stringove prebaciti na i18n ključeve.

2. **Type/API cleanup (legacy removal na FE strani)**
- U frontend tipovima i komponentama ukloniti preostale `quantity_kg`, `total_quantity_kg`, `consumed_*_kg` reference gdje backend više koristi canonical shape.
- Zadržati legacy samo gdje je eksplicitno potreban fallback, uz komentar.

3. **UI consistency polish**
- Potvrditi da su širine i razmaci konzistentni kroz sve module bez preklapanja sa sidebarom.

---

## Canonical backend contract (frontend mora pratiti)

- Orders:
  - `GET/POST /api/orders`
  - `GET/PUT /api/orders/<id>`
  - `DELETE /api/orders/<id>/lines/<line_id>`
- Approvals daily:
  - `GET /api/drafts/daily`
  - `GET /api/drafts/daily/<date>/<location_id>`
  - `POST /api/drafts/daily/<date>/<location_id>/approve`
  - `POST /api/drafts/daily/<date>/<location_id>/reject`
  - `PATCH /api/drafts/daily/<date>/<location_id>/lines`
- Identifikator:
  - `GET /api/identifikator/lookup?query=...`
  - `POST /api/identifikator/report`
  - `GET /api/admin/identifikator/queue`
  - `PATCH /api/admin/identifikator/queue/<id>`
- Inventory:
  - `GET /api/inventory`
  - `GET /api/inventory/<article_id>/inspect`
- Article update:
  - `PATCH /api/articles/id/<id>`
- Reports:
  - `GET /api/reports/inventurna`
  - `GET /api/reports/inventurna/export/excel|pdf`
  - `GET /api/reports/surplus`
  - `GET /api/reports/surplus/export/excel|pdf`
  - `GET /api/reports/statistics/consumption`
  - `GET /api/reports/statistics/top-consumers`
  - `GET /api/reports/statistics/reorder-risk`
  - `GET /api/reports/statistics/reporting`

---

## Acceptance Criteria

1. [ ] Nijedan ekran nema preklapanje contenta sa sidebarom na desktopu.
2. [ ] Svi P0 API mismatch-evi riješeni i runtime flowovi rade (Orders, Identifikator, Approvals, Receiving).
3. [ ] Sidebar i route guardovi su RBAC-konzistentni.
4. [ ] `/articles` više nije prisutan u navigaciji.
5. [ ] Orders create/edit podržava line-level workflow.
6. [ ] Reports i export flow rade preko stvarnog backend contracta.
7. [ ] Inventory ima category + state filtere prema planu.
8. [ ] UI je hrvatski-first bez kritičnih hardcoded EN stringova.
9. [ ] `npx tsc && npx vite build` prolazi.

---

## Verifikacija

### Automated

```bash
cd desktop-ui
npx tsc
npx vite build
```

### Manual (obavezno)

1. Layout smoke test: `Inventory`, `Orders`, `Reports`, `Approvals` na desktopu, bez overlapa sa sidebarom.
2. Role smoke test:
- ADMIN vidi admin module i može akcije.
- OPERATOR ne vidi/izvodi admin-only akcije.
3. Orders test:
- create order s lineovima,
- partial receive,
- close order na full receive.
4. Approvals day-flow:
- list, detail, edit aggregate, approve/reject.
5. Identifikator:
- lookup, missing report submit, admin queue patch.
6. Export:
- inventurna/surplus excel+pdf download kroz authenticated flow.

---

## Obavezni output agenta

- Summary po P0/P1/P2.
- Popis promijenjenih fileova.
- Točni API contracti koji su usklađeni.
- Rezultati builda i manual smoke checkova.
- Popis preostalih rizika (ako postoje).

