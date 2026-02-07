# WAREHOUSE SCALE AUTOMATION — MASTER PROJECT KNOWLEDGE FILE
(Complete architectural, business, and technical consolidation)

**VERSION:** 1.0  
**PURPOSE:** Permanent knowledge base snapshot  
**AUDIENCE:** Owner/Admin (Stefan), AI agents, future developers  
**SCOPE:** Entire system vision, architecture, logic, rules, decisions, constraints, and roadmap

---

## 1. PROJECT IDENTITY

**Project name:**  
Warehouse Scale Automation

**Core purpose:**  
Digital system for tracking paint/material consumption, stock, surplus, batches, and receiving in a production environment.

**Primary goal:**  
Replace manual tracking (Excel, memory, paper) with a structured, rule-based, traceable system.

**Key principle:**  
Rule-based system first. AI is NOT required for v1.

**This is an internal production tool — not a public SaaS.**

---

## 2. REAL-WORLD CONTEXT

The system is designed for a real paint usage workflow:

- **Materials (paints)** are stored in warehouse.
- Each paint has:
  - internal company code
  - supplier/manufacturer code
  - multiple names/aliases
- Each paint exists in **batches**.
- Each batch has **expiry date**.
- Painters consume paint.
- Weight is measured.
- Consumption must be approved.
- Stock must never go negative.
- Surplus exists (leftovers).
- Inventory counts happen.
- New goods arrive (receiving).
- Management wants insights later.

**Primary admin:**  
Stefan

**Operators:**  
Painters/lacquerers entering quantities.

**Hardware future:**  
Tablet + scale + barcode scanner.

**Current stage:**  
Software-first, hardware later.

---

## 3. CORE SYSTEM PHILOSOPHY

This system is designed around strict rules:

- **Nothing directly modifies stock** without a controlled workflow.
- **All changes must be logged** as transactions.
- **Approval logic is centralized.**
- **Surplus is consumed before stock.**
- **Stock never goes below zero.**
- **Admin has full control.**
- **Operators have minimal permissions.**

This ensures:
- traceability
- auditability
- predictability
- future automation readiness

---

## 4. USER ROLES (LOCKED)

### ADMIN (Stefan)
**Can:**
- Create articles
- Edit articles
- Manage aliases
- Create batches
- Receive stock
- Run inventory counts
- Approve/reject drafts
- View reports
- View full inventory
- Configure system
- Change own login credentials

### OPERATOR (tablet user)
**Can:**
- Select article
- Select batch
- Enter quantity
- Send draft

**Cannot:**
- Approve
- Edit articles
- See admin tools
- Modify inventory
- View reports

---

## 5. CORE DATA MODEL — CONCEPTUAL

**Entities:**
- Article (paint/material)
- Batch
- Stock
- Surplus
- Draft (weigh-in)
- Transaction
- User
- Location (fixed: ID=1, Code='13')

---

## 6. ARTICLE MODEL — BUSINESS DEFINITION

Article = one material/paint.

### Core identity (LOCKED):

- **article_no** (internal company code)  
  Example: 800147  
  UNIQUE  
  Primary reference

- **description** (full name)  
  Example: ALEXIT-FST Strukturlack 346-65/topcoat, 5339, cockpit blue AIC 5.7, semi-gloss (12kg)

- **is_active**
- **created_at**
- **updated_at**

### Additional business fields (v1 required):

- **uom** (KG / L)
- **manufacturer**
- **manufacturer_art_number**
- **aliases** (max 5)

### Aliases:
Alternative names from:
- customers
- documents
- internal naming

**Rules:**
- max 5 per article
- globally unique
- case-insensitive
- lookup-only (search assist)

**Example:**
Article 800147 may have aliases: `DS-M0050AGB1A25`, `DCIN800-DA5.7#LACK,STRUKTUR`

**Purpose:**
Search by alias → resolve correct article.

---

## 7. ARTICLE CODE vs MANUFACTURER CODE

**Important clarification:**

`article_no` = **INTERNAL company code**  
Example: 800147

`manufacturer_art_number` = **SUPPLIER code**  
Example: 34665.91B6.7.171

They are NOT the same.

---

## 8. BATCH MODEL

Each article exists in batches.

**Fields:**
- `batch_code`
- `article_id`
- `expiry_date`

**Batch code format:**
- Allowed:
  - 4–5 digits
  - 9–12 digits
- Examples: 0044, 0606, 1045, 292456953, 2924662112

**Expiry date:**
- REQUIRED for receiving workflow.

**System Batch (Consumables):**
- Syntax: `batch_code='NA'`
- Expiry: `2099-12-31`
- Used for: Non-batch-tracked items (consumables).
- Logic: Frontend sends `batch_id=null` for consumables; Backend maps to 'NA' batch.

---

## 9. STOCK vs SURPLUS

**Stock:**
Official quantity in warehouse.

**Surplus:**
Leftover material (extra/unused after work).

**Core rule:**
Consumption uses surplus first, then stock.

---

## 10. CONSUMPTION WORKFLOW

1. **Operator:** Enters quantity → creates DRAFT
2. **Admin:** Approves → system applies:
   - consume surplus
   - consume stock
   - create transactions
   - update inventory

---

## 11. RECEIVING WORKFLOW (CRITICAL)

New materials arrive.

**Admin inputs:**
- article
- batch_code
- quantity
- expiry_date

**System:**
- creates batch if needed
- increases stock
- logs STOCK_RECEIPT transaction

**Stock NEVER added via draft.**

---

## 12. INVENTORY COUNT LOGIC

Admin enters counted quantity.

**Three cases:**

1. **CASE 1 — counted > total**
   - Difference → surplus

2. **CASE 2 — counted = total**
   - No change

3. **CASE 3 — counted < total**
   - Shortage draft created
   - Admin must approve reduction.

Stock never negative.

---

## 13. TRANSACTION TYPES

- `WEIGH_IN`
- `SURPLUS_CONSUMED`
- `STOCK_CONSUMED`
- `INVENTORY_ADJUSTMENT`
- `INVENTORY_SHORTAGE`
- `STOCK_RECEIPT`

All inventory movement is tracked here.

---

## 14. INVENTORY SUMMARY VIEW

**Per:**
- article
- batch
- location

**Shows:**
- stock
- surplus
- total
- expiry
- updated_at

---

## 15. FUTURE REPORTING CAPABILITIES

Already possible from transaction data:
- top 20 consumed paints
- usage trends
- monthly consumption
- expiry tracking
- low stock alerts
- demand forecasting (later)

---

## 16. UI DESIGN PHILOSOPHY

**Admin UI:**
Full control dashboard.

**Operator UI:**
Ultra-simple. Touch optimized.

**Inventory UX:**
Color-coded:
- expired
- expiring
- low
- inactive

**Articles unused for 2 months:**
Visually different.

---

## 17. AUTHENTICATION

JWT-based.

**Access token:** ~15 minutes  
**Refresh token:** ~7 days

**Production:**
System must not start with weak secret.

**Admin can change:**
- username
- password

---

## 18. CURRENT SYSTEM MATURITY

**Already implemented:**
- articles
- aliases
- batches
- expiry tracking
- drafts
- approval engine
- surplus-first logic
- inventory summary
- receiving
- reports foundation
- JWT auth
- RBAC

**Missing polish:**
- inventory UX refinement
- reports UI improvements
- Excel export
- inactive highlighting
- alias conflict preview

---

## 19. HARDWARE ROADMAP

**Future integration:**
- Raspberry Pi backend host
- Windows tablet UI
- Barcode scanner
- Scale input

Architecture already supports this.

---

## 20. SYSTEM ROLE IN FUTURE

This can evolve into:
- production tracking
- time estimation
- scheduling assistant
- stock planning system
- decision support system

Without AI initially.

---

## 21. WHAT MUST NEVER BE BROKEN

These are "LOCKED":
- surplus-first consumption
- approval-based changes
- transaction logging
- stock never negative
- alias uniqueness
- batch expiry tracking
- role separation

---

## 22. PROJECT STRATEGIC DIRECTION

**Phase 1:** Stable inventory + consumption  
**Phase 2:** Receiving + reporting  
**Phase 3:** Optimization insights  
**Phase 4:** Production orchestration

---
**END OF MASTER KNOWLEDGE FILE**
