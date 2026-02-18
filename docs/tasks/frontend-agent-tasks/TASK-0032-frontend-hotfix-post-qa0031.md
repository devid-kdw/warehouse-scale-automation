# Task Brief: TASK-0032 — Frontend Hotfix After QA-0031

**Created**: 2026-02-18  
**Assigned to**: Frontend Agent (hotfix)  
**Status**: Ready  
**Priority**: P0

---

## Goal

Zatvoriti failove iz `QA-0031-browser-regression-2026-02-18.md` i ukloniti preostale kritične UX/RBAC greške prije ponovnog full retesta.

---

## Inputs (must use)

1. `docs/status/QA-0031-browser-regression-2026-02-18.md`
2. `/Users/grzzi/.gemini/antigravity/brain/d1af48d0-c1ec-4151-8db2-43edf71129d6/walkthrough.md.resolved`
3. `docs/team/RULES_OF_ENGAGEMENT.md`
4. `docs/team/DECISIONS.md`
5. `docs/tasks/frontend-agent-tasks/TASK-0030-frontend-remediation-contract-layout-rbac.md`
6. `docs/tasks/frontend-agent-tasks/TASK-0030B-frontend-remediation-delta.md`

---

## Confirmed Issues From QA-0031

1. `T05` i18n gaps (EN stringovi i dalje prisutni)
2. `T08` Create Order flow šalje payload bez line stavki (`422`)
3. `T18/T19` RBAC leak: OPERATOR vidi i može otvoriti `Postavke`

---

## P0 (must fix first)

### 1) RBAC hardening for Settings

Files:
- `desktop-ui/src/components/Sidebar.tsx`
- `desktop-ui/src/App.tsx`

Required:
- `Postavke` link ne smije biti vidljiv OPERATOR-u.
- Ruta `/settings` mora biti zaštićena admin guardom (`RequireAdmin`), ne samo `RequireAuth`.
- Ako OPERATOR ručno upiše `/#/settings`, mora biti redirect bez pristupa sadržaju.

### 2) Orders create flow must satisfy backend contract

Files:
- `desktop-ui/src/pages/Orders/CreateOrder.tsx`
- `desktop-ui/src/api/orders.ts`
- `desktop-ui/src/api/types.ts` (ako treba proširenje tipova)

Required:
- U `CreateOrder` mora postojati line-entry UX (minimalno 1 line obavezan):
  - `article_id`
  - `ordered_qty`
  - `uom`
  - `delivery_date` (optional)
  - `note` (optional)
- Frontend ne smije slati `lines: []`.
- Prije submita validirati da postoji barem jedan ispravan red.
- Zadržati postojeću auto/manual logiku za `order_number`.

---

## P1 (complete in same task)

### 3) Croatian-first i18n completion (core screens)

Files (minimum):
- `desktop-ui/src/pages/Login.tsx`
- `desktop-ui/src/pages/Orders/CreateOrder.tsx`
- `desktop-ui/src/pages/Settings.tsx`
- `desktop-ui/src/components/common/*` (gdje su hardcoded stringovi)
- locale fajlovi u `desktop-ui/src/i18n/locales/*/common.json`

Required:
- Ukloniti preostale hardcoded EN stringove iz glavnih flowova.
- Svi ključni UI tekstovi moraju ići preko i18n ključeva.
- Hrvatski prijevodi moraju biti potpuni i gramatički ispravni.

---

## Non-negotiable rules

1. Ne mijenjati backend kod ni API ugovore.
2. Ako naiđeš na mismatch docs/backend, backend implementation je canonical za frontend klijent.
3. Ne uvoditi novi UX scope izvan ova 3 confirmed issue-a.
4. Ne uklanjati postojeće featuree koji rade.

---

## Acceptance Criteria

1. [ ] OPERATOR ne vidi `Postavke` u sidebaru.
2. [ ] OPERATOR ne može otvoriti `/settings` direktnim URL-om.
3. [ ] `CreateOrder` ne može submitati order bez line stavke.
4. [ ] Uspješan submit ordera radi s barem 1 line stavkom (bez 422 zbog praznih lines).
5. [ ] Preostali EN stringovi iz core flowova zamijenjeni su i18n ključevima.
6. [ ] `npx tsc && npx vite build` prolazi.

---

## Verification (required)

### Automated

```bash
cd desktop-ui
npx tsc
npx vite build
```

### Manual

1. Login kao `OPERATOR`:
- nema `Postavke` linka,
- `/#/settings` nije dostupno.
2. Login kao `ADMIN`:
- `Postavke` i dalje dostupne.
3. Orders:
- pokušaj create bez lineova -> frontend validacija blokira submit,
- create s lineom -> success i otvaranje detail view.
4. Spot-check ključnih ekrana da su HR stringovi prikazani.

---

## Required Agent Output

1. Sažetak po P0/P1.
2. Lista promijenjenih fileova.
3. Build rezultati.
4. Manual test rezultati za 4 obavezne točke.
5. Preostali rizici/blokade (ako postoje).

