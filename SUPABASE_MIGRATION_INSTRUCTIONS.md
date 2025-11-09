# Supabase Migration Instructions

## Changes Needed for Multiple Custom Interventions

The backend code has been updated to parse multiple interventions (separated by newlines) and store each one separately in the `custom_interventions` table.

### Required Migration

Run the migration script: `backend/migrations/fix_custom_interventions_tables.sql`

This script will:
1. ✅ Rename `customer_user_interventions` → `user_interventions` (if needed)
2. ✅ Create `custom_interventions` table with proper schema
3. ✅ Add indexes for performance
4. ✅ Add RLS policies for security
5. ✅ Add triggers for `updated_at` timestamp

### Table Schema

The `custom_interventions` table will have:
- `id` (UUID, primary key, auto-generated)
- `user_id` (UUID, foreign key to auth.users)
- `intake_id` (UUID, foreign key to intakes)
- `intervention_name` (TEXT) - **Each intervention stored separately**
- `description` (TEXT, nullable)
- `context` (TEXT, nullable)
- `status` (TEXT, default 'pending')
- `reviewed_by` (UUID, nullable)
- `reviewed_at` (TIMESTAMPTZ, nullable)
- `notes` (TEXT, nullable)
- `created_at` (TIMESTAMPTZ, auto-generated)
- `updated_at` (TIMESTAMPTZ, auto-updated)

### How to Apply

1. **Open Supabase Dashboard** → SQL Editor
2. **Copy the entire contents** of `backend/migrations/fix_custom_interventions_tables.sql`
3. **Paste and run** the script
4. **Verify** the table was created:
   ```sql
   SELECT * FROM custom_interventions LIMIT 5;
   ```

### What Happens After Migration

When a user enters multiple interventions in the intake form (separated by newlines):
- Each line becomes a separate record in `custom_interventions`
- All records link to the same `intake_id` and `user_id`
- Each has its own `id`, `intervention_name`, and `status`

### Example

**User Input:**
```
i tried hot water every morning
i tried savoury breakfast instead of sweet breakfast
```

**Result in Database:**
- Record 1: `intervention_name = "i tried hot water every morning"`
- Record 2: `intervention_name = "i tried savoury breakfast instead of sweet breakfast"`

Both records will have:
- Same `user_id`
- Same `intake_id`
- Same `status = 'pending'`
- Different `id` (UUID)
- Different `created_at` timestamps

### No Additional Changes Needed

The migration script is **idempotent** (safe to run multiple times) and handles:
- ✅ Table creation (if doesn't exist)
- ✅ Index creation (if doesn't exist)
- ✅ Trigger creation (replaces if exists)
- ✅ RLS policy setup (replaces if exists)

**Just run the migration script once in Supabase SQL Editor!**

