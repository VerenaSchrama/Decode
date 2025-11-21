# Why 'abandoned' Status is Not Allowed

## The Problem

The database has a **CHECK constraint** called `intervention_periods_status_check` that restricts which values can be stored in the `status` column of the `intervention_periods` table.

## What is a CHECK Constraint?

A CHECK constraint is a database-level rule that validates data before it's inserted or updated. It ensures data integrity by only allowing specific values.

## Current Constraint

The constraint `intervention_periods_status_check` was likely created when the table was first set up and only allows:
- `'active'`
- `'completed'`  
- `'paused'`

It does **NOT** allow `'abandoned'`.

## Why the Mismatch?

The documentation and code mention `'abandoned'` as a valid status, but the database constraint was never updated to include it. This is a **schema mismatch** between:
- **Code/Documentation**: Expects `'abandoned'` to be valid
- **Database Schema**: Only allows `'active'`, `'completed'`, `'paused'`

## Current Workaround

We're using `'completed'` status with a note indicating it was changed:
```python
'status': 'completed',
'notes': 'Completed (changed): User changed to new intervention'
```

This works because `'completed'` is allowed by the constraint.

## Proper Fix (If You Want 'abandoned' Status)

To properly support `'abandoned'` status, you would need to **alter the database constraint** in Supabase:

### Option 1: Add 'abandoned' to the constraint

```sql
-- First, drop the existing constraint
ALTER TABLE intervention_periods 
DROP CONSTRAINT intervention_periods_status_check;

-- Then, recreate it with 'abandoned' included
ALTER TABLE intervention_periods 
ADD CONSTRAINT intervention_periods_status_check 
CHECK (status IN ('active', 'completed', 'paused', 'abandoned'));
```

### Option 2: Check current constraint definition

First, see what the constraint currently allows:

```sql
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conname = 'intervention_periods_status_check';
```

This will show you the exact CHECK condition.

## Recommendation

**For now, the workaround (using 'completed' with a note) is fine** because:
1. ✅ It works immediately without database changes
2. ✅ The note clearly indicates the intervention was changed
3. ✅ You can still query and filter by status
4. ✅ No data migration needed

**If you want to add 'abandoned' later**, you can:
1. Run the SQL migration in Supabase SQL Editor
2. Update the code to use `'abandoned'` instead of `'completed'`
3. Update any existing records if needed

## How to Check the Constraint in Supabase

1. Go to Supabase Dashboard
2. Navigate to **Table Editor** → `intervention_periods` table
3. Click on the `status` column
4. Look for **Constraints** or **Check Constraints**
5. You'll see the allowed values there

Or use the SQL Editor:
```sql
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'intervention_periods'::regclass
AND conname LIKE '%status%';
```

