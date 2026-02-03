# Task Brief: TASK-XXX-Short-Name

**Created**: YYYY-MM-DD  
**Assigned to**: [Frontend Agent | Backend Agent | Both]  
**Status**: [Planning | In Progress | Testing | Done]  
**Priority**: [P0-Critical | P1-High | P2-Medium | P3-Low]

---

## 🎯 Goal

_(What does the user/business get from this feature? One clear sentence.)_

Example: "Admin can receive new stock arrivals and automatically update inventory with proper audit trail."

---

## 📋 Scope

### In Scope
- Feature/component 1
- Feature/component 2
- Specific behavior X

### Out of Scope
- Thing that's NOT included in this task
- Future enhancement Y
- Related but separate feature Z

---

## 🔧 Technical Changes

### Backend Changes (if applicable)

#### API Endpoints
- **New**: `POST /api/inventory/receive`
  - Auth: ADMIN only
  - Request: `{location_id, article_id, batch_code, quantity_kg, expiry_date, note}`
  - Response: `{batch_id, quantity_received, new_stock_total, transaction}`
  
- **Modified**: (list if existing endpoints change)

#### Database Changes
- Migration needed: [Yes | No]
- Tables affected: `stock`, `batches`, `transactions`
- New transaction type: `STOCK_RECEIPT`

#### Service Layer
- New service function: `receive_stock()`
- Modified services: (list if applicable)

### Frontend Changes (if applicable)

#### New Pages/Components
- `ReceiveStock.tsx` - form for stock receiving
- `ReceiveStockModal.tsx` - alternative modal implementation

#### Modified Pages
- (list existing pages that need updates)

#### API Client
- Add `receiveStock()` function to `src/api/services.ts`
- Add types: `ReceiveStockPayload`, `ReceiveStockResponse`

---

## ✅ Acceptance Criteria

_(Clear, measurable criteria. Each item should be testable.)_

1. [ ] Admin can navigate to "Receive Stock" page
2. [ ] Form validates: article required, batch code format, quantity > 0, expiry required
3. [ ] Submitting form increases stock.quantity_kg for correct location/article/batch
4. [ ] Transaction with type=STOCK_RECEIPT is created
5. [ ] If batch exists with different expiry → 409 error with clear message
6. [ ] Success notification shown, inventory view refreshes
7. [ ] Operator role CANNOT access receive stock feature

---

## 🧪 Test Plan

### Manual Testing

1. **Happy Path - New Batch**:
   ```
   1. Login as admin
   2. Navigate to Receive Stock
   3. Select article 800147
   4. Enter batch code: 0607
   5. Enter quantity: 8.00 kg
   6. Enter expiry: 2026-06-15
   7. Submit
   Expected: Success, stock increased by 8.00, transaction recorded
   ```

2. **Expiry Mismatch**:
   ```
   1. Receive same batch (0607) with different expiry
   Expected: 409 error, message shows existing expiry vs provided expiry
   ```

3. **Validation**:
   ```
   1. Try to submit without expiry
   Expected: Validation error "Expiry date is required"
   
   2. Try negative quantity
   Expected: Validation error
   ```

4. **RBAC**:
   ```
   1. Login as operator
   2. Try to access /receive route
   Expected: Redirect to /drafts/new (no access)
   ```

### Automated Tests (if applicable)

```bash
# Backend
pytest backend/tests/test_receiving.py -v

# Frontend
npm test -- ReceiveStock.test.tsx
```

---

## 🚀 Rollout Notes

### Prerequisites
- Database migration applied (if needed)
- `STOCK_RECEIPT` transaction type added to backend
- Admin role exists in users table

### Deployment Steps
1. Apply database migration: `flask db upgrade`
2. Restart backend
3. Deploy frontend
4. Test manually with smoke test scenarios

### Configuration
- No new environment variables needed
- (or list new .env vars if applicable)

### Seed Data
- Ensure location with code="13" exists
- Ensure at least one ADMIN user exists

---

## 📚 Related Documentation

- [Receiving Spec Addendum](file:///Users/grzzi/.gemini/antigravity/brain/773ef5d2-4f66-4a78-8a70-e2251cebe334/receiving_spec_addendum.md)
- [DECISIONS.md - Batch Expiry Rules](../team/DECISIONS.md#batch-expiry-mismatch-policy)
- [CHANGELOG.md](../team/CHANGELOG.md)

---

## 📝 Implementation Notes

_(Space for agent to add notes during implementation)_

- 

---

**Status Updates**:
- YYYY-MM-DD: Task created
- YYYY-MM-DD: Backend implementation started
- YYYY-MM-DD: Frontend implementation complete
- YYYY-MM-DD: Testing complete, ready for review
