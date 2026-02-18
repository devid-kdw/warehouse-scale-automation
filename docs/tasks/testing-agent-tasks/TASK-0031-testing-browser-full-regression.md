# Task Brief: TASK-0031 — Browser Full Regression & Functional Verification

**Created**: 2026-02-18  
**Assigned to**: Testing Agent  
**Status**: Ready  
**Priority**: P0

---

## Goal

Provesti kompletno browser testiranje cijele aplikacije (Admin + Operator tokovi gdje su dostupni), potvrditi da funkcije rade po važećim pravilima i zapisati rezultate u jedinstveni QA izvještaj.

---

## Scope

Ovaj task pokriva:
- funkcionalno testiranje svih glavnih modula,
- RBAC testiranje (`ADMIN` vs `OPERATOR`),
- provjeru API ugovora kroz browser network tokove,
- vizualno/layout testiranje (uključujući sidebar/content preklapanje),
- regresiju nakon backend + frontend remediation valova.

Ovaj task ne pokriva:
- code fixeve,
- migracije,
- direktne DB izmjene.

---

## Preconditions

1. Backend dostupan na `http://localhost:5001`.
2. Frontend (web) dostupan na `http://localhost:5173` ili Electron app pokrenut.
3. Test korisnik ADMIN:
   - username: `stefan`
   - password: `ChangeMe123!`
4. Ako `OPERATOR` korisnik ne postoji, to označiti kao **BLOCKED** za RBAC-Operator scenarije (ne kreirati direktno u bazi).

---

## Required Reading (before test execution)

1. `README.md`
2. `docs/team/TESTING_AGENT_RULES.md`
3. `docs/team/RULES_OF_ENGAGEMENT.md`
4. `docs/team/DECISIONS.md`
5. `docs/tasks/TASK-0020-ui-feedback-master-plan-input.md`
6. `docs/tasks/TASK-0021-v3-implementation-master-plan.md`
7. `docs/tasks/frontend-agent-tasks/TASK-0030-frontend-remediation-contract-layout-rbac.md`
8. `docs/tasks/frontend-agent-tasks/TASK-0030B-frontend-remediation-delta.md`
9. `docs/team/CHANGELOG.md`

---

## Test Matrix (mandatory)

| ID | Area | Scenario | Expected |
|---|---|---|---|
| T01 | App shell/layout | Sidebar + content na svim glavnim ekranima | Nema preklapanja; content nije zaklonjen sidebarom |
| T02 | Auth | Login s validnim ADMIN credentialima | Uspješan login + ispravan landing |
| T03 | Auth | Login s neispravnim credentialima | Jasna greška bez rušenja UI |
| T04 | Navigation | Otvaranje svih modula iz menija | Svaka ruta se učitava bez runtime errora |
| T05 | i18n | Hrvatski tekstovi kroz ključne tokove | Nema kritičnih hardcoded EN stringova u glavnim ekranima |
| T06 | Automatski unos | Kreiranje draft unosa (scale/manual fallback) | Draft se kreira i vidljiv je u odobrenjima |
| T07 | Izlaz robe | Kreiranje izlazne liste s više redaka | Generira se `receipt_number`, zapis spremljen |
| T08 | Orders | Kreiranje narudžbe (manual + auto broj) s line stavkama | Order spremljen, broj unikatan, line podaci točni |
| T09 | Orders/Receiving | Djelomično zaprimanje po `order_line_id` + `delivery_note_number` | Open order ostaje otvoren dok nisu sve stavke zaprimljene |
| T10 | Receiving ad-hoc | Ulaz robe bez narudžbe (uz napomenu) | Zaprimanje uspješno i audit zapisan |
| T11 | Skladište | Filter kategorije + Active/Inactive/All + search | Filtri rade, rezultati konzistentni |
| T12 | Skladište | Inspect article + Edit article (ADMIN) | Podaci točni; edit ne ruši inventurne logike |
| T13 | Odobrenja | Daily list, detail, edit agregata, approve/reject day | Grupiranje i akcije rade bez mismatcha |
| T14 | Identifikator | Lookup + prijava nepostojećeg artikla | Lookup radi; report submit radi |
| T15 | Missing Items/Admin queue | Obrada OPEN prijava (resolve/close tok) | Status lifecycle radi i vidi se u listi |
| T16 | Izvještaji | Inventurna lista, Surplus lista, Statistike | Ekrani se učitavaju i podaci su konzistentni |
| T17 | Exporti | Excel/PDF export (gdje dostupno) | Download radi ili jasna backend greška (ne rušenje UI) |
| T18 | RBAC Operator | Operator pristup dozvoljenim modulima | Operator može samo dozvoljene tokove |
| T19 | RBAC Operator | Operator pristup ADMIN-only modulima | Pristup onemogućen (UI i route guard) |
| T20 | Audit behavior | Nakon stock-changing akcija provjera transaction refleksije u UI/reporting tokovima | Podaci konzistentni i očekivani |

---

## API Contract Spot-Checks (mandatory via browser network)

Provjeriti da frontend poziva canonical backend rute:
- `/api/orders/*`
- `/api/drafts/daily*`
- `/api/admin/identifikator/queue*`
- `/api/inventory*`
- `/api/reports/*`

Za svaki mismatch zapisati:
- ekran + akcija,
- stvarni request URL/payload,
- response status/body,
- očekivani contract.

---

## Evidence Rules

1. Za svaki **FAIL** i **BLOCKED** obavezno priložiti screenshot i korake reprodukcije.
2. Evidenciju spremati pod:
   - `docs/status/evidence/task-0031/`
3. QA izvještaj mora sadržavati reference na screenshot fajlove.

---

## Required Deliverable

Testing Agent mora kreirati izvještaj:

- `docs/status/QA-0031-browser-regression-YYYY-MM-DD.md`

Izvještaj mora sadržavati:
- scope i environment,
- pass/fail/block count,
- rezultat svake stavke T01-T20,
- detaljnu listu bugova (`Severity: Blocker/High/Medium/Low`),
- listu blokera i što nedostaje za nastavak,
- zaključak: `READY_FOR_RELEASE` ili `NOT_READY`.

---

## Exit Criteria

Task je završen tek kad:
1. Svi testovi iz matrice imaju status (`PASS`, `FAIL`, ili `BLOCKED`).
2. QA report dokument je spremljen na traženoj putanji.
3. Svi failovi imaju reproducibilne korake.
4. Donesen je jasan go/no-go zaključak.

