# Project Dashboard

**Project**: Warehouse Paint Inventory Management  
**Last Updated**: 2026-02-03  
**Status**: 🟡 Active Development (v1 → Production Readiness)

---

## 📊 What We're Working On Today

### Current Focus: **Core Inventory Features for Production Use**

**Priority #1**: Making the system usable in the warehouse **tomorrow**.

We're focusing on:
1. ✅ **Consumption tracking** (draft → approve workflow) — DONE
2. 🔄 **Receiving workflow** (adding new batches + stock) — NEXT
3. 🔄 **Expiry tracking** (showing warnings for batches <30 days) — NEXT
4. 🔄 **Inventory read endpoints** (view current stock levels) — NEXT
5. 🔄 **Transaction reports** (audit trail view) — AFTER MVP

**NOT focusing on** (enterprise hardening comes later):
- ❌ Prometheus/monitoring
- ❌ Rate limiting
- ❌ Multi-location support
- ❌ HTTPS hardening
- ❌ Advanced backup automation

---

## ✅ What's Done

### Phase 0: Foundation (Completed)

- ✅ **Backend architecture** with Flask + PostgreSQL
- ✅ **JWT authentication** with ADMIN/OPERATOR roles
- ✅ **Draft approval workflow**:
  - Operator creates draft (WEIGH_IN or INVENTORY_SHORTAGE)
  - Admin approves/rejects
  - Surplus-first consumption logic
  - Row-level locking for concurrency
- ✅ **Audit trail**: All stock changes logged in `transactions` table
- ✅ **Desktop UI** with Electron + React + Mantine
- ✅ **Database migrations** working and tracked in Git
- ✅ **Batch expiry field** in database (ready to use)
- ✅ **Article aliases** for lookup shortcuts (max 5 per article)

### Phase 1: Team Setup (Just Completed)

- ✅ **Multi-agent documentation**:
  - `docs/team/AGENTS.md` — Role definitions
  - `docs/team/RULES_OF_ENGAGEMENT.md` — Locked rules
  - `docs/team/WORKFLOW.md` — Development process
  - `docs/team/PROJECT_DASHBOARD.md` — This file

---

## 🔄 What's Next

### Phase 2: Receiving Workflow (HIGHEST PRIORITY)

**Why**: Currently can only consume stock, can't add new batches!

**What we need**:
- Backend: `RECEIPT` transaction type
- Backend: `POST /api/receiving` endpoint
- Backend: Service to create batch + add stock
- Frontend: "Receiving" page (ADMIN only)
- Frontend: Form with Article, Batch Code, Quantity, Expiry Date
- Tests: E2E flow (receive → verify stock increase)

**Estimated**: 1-2 days

---

### Phase 3: Inventory Read & Expiry Warnings

**What we need**:
- Backend: `GET /api/inventory/current` endpoint (current stock by article/batch)
- Frontend: Inventory view page with expiry warnings
- Frontend: Highlight batches expiring in <30 days
- Tests: Ensure expiry calculation correct

**Estimated**: 1 day

---

### Phase 4: Transaction Reports View

**What we need**:
- Backend: `GET /api/transactions` with filters (date range, article, type)
- Frontend: Transaction log page (ADMIN only)
- Frontend: Export to Excel (SAP template)
- Tests: Verify filtering works

**Estimated**: 1-2 days

---

## 🚨 Risks & Open Questions

### Critical Issues

| Issue | Impact | Status | Owner |
|-------|--------|--------|-------|
| No receiving workflow | Can't add stock! | 🔴 BLOCKER | Backend Agent |
| Expiry not shown in UI | Can't see batch expiration | 🟡 HIGH | Frontend Agent |
| No inventory view yet | Can't see current stock levels | 🟡 HIGH | Backend + Frontend |

### Open Questions

1. **Batch code enforcement**: Should we enforce format validation (4-5 or 9-12 digits) in UI or allow exceptions?
   - **Decision needed by**: Stefan
   - **Impact**: User experience (strictness vs flexibility)

2. **Receiving permissions**: Should OPERATOR be able to receive, or ADMIN only?
   - **Current assumption**: ADMIN only (operators only do consumption drafts)
   - **To confirm**: Stefan

3. **Expiry enforcement**: Should system prevent receiving of already-expired batches?
   - **Current assumption**: Allow but show warning
   - **To confirm**: Stefan

---

## 📈 Production Readiness Checklist

### Core Functionality
- [x] User login (JWT authentication)
- [x] Create consumption draft (OPERATOR)
- [x] Approve/reject draft (ADMIN)
- [x] Stock deduction on approval
- [x] Audit trail logging
- [ ] Receive new batches ⬅️ **NEXT**
- [ ] View inventory levels ⬅️ **NEXT**
- [ ] Expiry warnings ⬅️ **NEXT**
- [ ] Transaction reports ⬅️ **SOON**

### Data Quality
- [x] Migrations reproducible from scratch
- [x] Stock never goes negative (database constraint)
- [x] Batch code validation (format check)
- [x] Surplus-first consumption enforced
- [ ] Initial stock data loaded (location 13)

### Security
- [x] JWT secret validation (can't start with default in prod)
- [x] Role-based access control (ADMIN vs OPERATOR)
- [x] Password hashing (users table)
- [ ] HTTPS setup (deployment phase)
- [ ] Token refresh flow tested

### Deployment
- [ ] PostgreSQL backup script
- [ ] Deployment guide (Raspberry Pi)
- [ ] systemd service file
- [ ] nginx reverse proxy config
- [ ] Environment variables documented

### Testing
- [x] Backend pytest suite (approval, auth, validation)
- [x] Basic frontend flows manual tested
- [ ] E2E test: login → create draft → approve → verify stock ⬅️ **IMPORTANT**
- [ ] Load test: concurrent approvals
- [ ] Migration rollback tested

---

## 🎯 Sprint Planning

### This Week (2026-02-03 to 2026-02-09)

**Goal**: Unlock core inventory operations

- [ ] **TASK-0001**: Implement receiving workflow (Backend + Frontend)
- [ ] **TASK-0002**: Add inventory view endpoint (Backend)
- [ ] **TASK-0003**: Display expiry warnings in UI (Frontend)

**Success Criteria**: Can receive batches, see stock levels, see expiry warnings

---

### Next Week (2026-02-10 to 2026-02-16)

**Goal**: Reports and audit trail UI

- [ ] **TASK-0004**: Transaction reports endpoint (Backend)
- [ ] **TASK-0005**: Transaction log UI (Frontend)
- [ ] **TASK-0006**: Excel export functionality

**Success Criteria**: Can export transaction history to Excel

---

### Week 3 (2026-02-17 to 2026-02-23)

**Goal**: Production hardening

- [ ] **TASK-0007**: E2E test suite
- [ ] **TASK-0008**: Deployment documentation
- [ ] **TASK-0009**: Backup script + restore testing

**Success Criteria**: Ready for Raspberry Pi deployment

---

## 💬 Agent Status Updates

### Backend Agent
- **Last Update**: 2026-02-03
- **Status**: 🟢 Ready for TASK-0001 (Receiving workflow)
- **Blockers**: None

### Frontend Agent
- **Last Update**: 2026-02-03
- **Status**: 🟢 Ready for TASK-0001 UI
- **Blockers**: Waiting for backend endpoint

### Orchestrator
- **Last Update**: 2026-02-03
- **Status**: 🟢 Documentation complete
- **Next**: Create TASK-0001 brief

---

## 📞 Key Contacts

- **Project Owner**: Stefan
- **Backend Agent**: AI (Backend focus)
- **Frontend Agent**: AI (Frontend focus)
- **Orchestrator**: AI (Coordination)

---

## 📚 Quick Links

- [Project Specification](../PROJECT_SPECIFICATION.md)
- [Agent Roles](./AGENTS.md)
- [Locked Rules](./RULES_OF_ENGAGEMENT.md)
- [Workflow Process](./WORKFLOW.md)
- [Backend README](../../backend/README.md)
- [Frontend README](../../desktop-ui/README.md)

---

## 🔄 Change Log

| Date | Change | Who |
|------|--------|-----|
| 2026-02-03 | Initial dashboard created | Orchestrator |
| 2026-02-03 | Added team documentation structure | Orchestrator |
