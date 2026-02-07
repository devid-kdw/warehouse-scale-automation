# Database Migrations Log

This document tracks all database schema migrations for the Warehouse Scale Automation project.

Format: **Migration Name** | **What Changed** | **Backwards Compatible** | **Apply/Rollback**

---

## Existing Migrations

### add_draft_groups - Draft Groups and Backfill
**File**: `backend/migrations/versions/add_draft_groups_manual.py`

**What Changed**:
- Created `draft_groups` table.
- Added `draft_group_id` FK to `weigh_in_drafts`.
- **Data Migration**: Automatically backfilled all existing drafts into new individual groups.
- Added indices for group-based lookups and status filtering.

**Backwards Compatible**: ✅ Yes - v1 API automatically wraps drafts in groups.

**How to Apply**:
```bash
cd backend
export FLASK_APP=run.py
venv/bin/python3 -m flask db upgrade
```

**How to Rollback**:
```bash
venv/bin/python3 -m flask db downgrade add_draft_groups
```

---

### c1d4f113222c - Initial Migration
**File**: `backend/migrations/versions/c1d4f113222c_initial_migration.py`

**What Changed**: 
- Created all core tables: `users`, `locations`, `articles`, `batches`, `stock`, `surplus`, `weigh_in_drafts`, `approval_actions`, `transactions`
- Established foreign key relationships
- Added unique constraints: `(location_id, article_id, batch_id)` for stock/surplus, `client_event_id` for drafts
- Created indexes on transactions table: `occurred_at`, `(article_id, occurred_at)`, `(batch_id, occurred_at)`

**Backwards Compatible**: N/A (initial schema)

**How to Apply**:
```bash
cd backend
flask db upgrade
```

**How to Rollback**:
```bash
flask db downgrade c1d4f113222c
```

**Notes**: This is the base schema. All tables must exist before any other migrations.

---

### f11e5d13d9f6 - Add Password Hash to Users
**File**: `backend/migrations/versions/f11e5d13d9f6_add_password_hash_to_users.py`

**What Changed**: 
- Added `password_hash` column to `users` table (nullable=True for backward compat)
- Enables JWT authentication with username/password

**Backwards Compatible**: ✅ Yes - column is nullable

**How to Apply**:
```bash
flask db upgrade
```

**How to Rollback**:
```bash
flask db downgrade f11e5d13d9f6
```

**Notes**: After applying, run `flask seed` to set default passwords for users.

---

### a3f5e8b2c1d4 - Add Article Expansion, Aliases, Draft Type
**File**: `backend/migrations/versions/a3f5e8b2c1d4_add_article_expansion_aliases_draft_type.py`

**What Changed**:
- Added `article_aliases` table for alternative article codes/barcodes
- Added `draft_type` column to `weigh_in_drafts` (values: `WEIGH_IN`, `INVENTORY_SHORTAGE`)
- Expanded article metadata fields (if applicable)

**Backwards Compatible**: ✅ Mostly - `draft_type` has default value `WEIGH_IN`

**How to Apply**:
```bash
flask db upgrade
```

**How to Rollback**:
```bash
flask db downgrade a3f5e8b2c1d4
```

**Notes**: Existing drafts automatically get `draft_type='WEIGH_IN'` default.

---

## Pending Migrations

### STOCK_RECEIPT Transaction Type
**Status**: ⏳ Planned

**What Will Change**:
- Add `STOCK_RECEIPT` to valid transaction types enum/validation
- No schema change required (tx_type is text column)
- Code change only: `Transaction.TX_STOCK_RECEIPT = 'STOCK_RECEIPT'`

**Backwards Compatible**: ✅ Yes - existing data unaffected

**How to Apply**: Code deployment only (no DB migration needed)

---

## Migration Best Practices

1. **Always test migrations** on dev database before production
2. **Backup production DB** before applying migrations
3. **Use transactions** - all migrations should be atomic
4. **Write reversible migrations** - provide downgrade path when possible
5. **Document data migrations** - if migration modifies existing data, note it here

## Migration Commands Reference

```bash
# Create new migration
flask db migrate -m "Description of change"

# Apply all pending migrations
flask db upgrade

# Rollback one migration
flask db downgrade -1

# Rollback to specific version
flask db downgrade <revision_id>

# Show current version
flask db current

# Show migration history
flask db history
```

---

## Migration Checklist

Before applying migration to production:

- [ ] Test on local dev database
- [ ] Backup production database
- [ ] Review migration SQL (check for table locks, data loss)
- [ ] Verify rollback path exists
- [ ] Check application compatibility (code changes needed?)
- [ ] Plan downtime window (if needed)
- [ ] Document in this file
- [ ] Update CHANGELOG.md
