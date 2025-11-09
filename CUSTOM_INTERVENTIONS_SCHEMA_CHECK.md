# Custom Interventions Table Schema Verification

## Existing Table Schema (from Supabase)

Based on the table you showed, the `custom_interventions` table has:
- ✅ `id` (uuid, primary key)
- ✅ `user_id` (uuid)
- ✅ `intake_id` (uuid)
- ✅ `intervention_name` (text)
- ✅ `description` (text, nullable)
- ✅ `context` (text, nullable)
- ✅ `status` (text)
- ✅ `reviewed_by` (uuid, nullable)
- ✅ `reviewed_at` (timestamptz, nullable)
- ✅ `notes` (text, nullable)
- ✅ `created_at` (timestamptz)
- ✅ `updated_at` (timestamptz)

## Backend Code Requirements

The backend code (`simple_intake_service.py`) inserts:
- ✅ `user_id` → matches `user_id` column
- ✅ `intake_id` → matches `intake_id` column
- ✅ `intervention_name` → matches `intervention_name` column
- ✅ `description` → matches `description` column
- ✅ `context` → matches `context` column
- ✅ `status` → matches `status` column

## Conclusion

**✅ The table schema is PERFECTLY ALIGNED!**

No changes are needed. The existing table structure already supports:
- ✅ Multiple records (each with unique `id`)
- ✅ All required fields that the backend inserts
- ✅ Proper data types (UUID for IDs, TEXT for names/descriptions)

## What to Verify (Optional)

You may want to check if these exist (they're nice to have but not required for basic functionality):

1. **Foreign Key Constraints:**
   ```sql
   SELECT constraint_name, constraint_type 
   FROM information_schema.table_constraints 
   WHERE table_name = 'custom_interventions';
   ```
   Should have foreign keys to `auth.users` and `intakes`

2. **Indexes:**
   ```sql
   SELECT indexname FROM pg_indexes 
   WHERE tablename = 'custom_interventions';
   ```
   Recommended: indexes on `user_id`, `intake_id`, and `status`

3. **RLS Policies:**
   ```sql
   SELECT policyname FROM pg_policies 
   WHERE tablename = 'custom_interventions';
   ```
   Should have policies for user access

4. **Status CHECK Constraint:**
   ```sql
   SELECT constraint_name, check_clause 
   FROM information_schema.check_constraints 
   WHERE constraint_name LIKE '%custom_interventions%status%';
   ```
   Should restrict status to: 'pending', 'reviewed', 'approved', 'rejected'

## Ready to Use

The table is ready! The backend code will now:
1. Parse multiple interventions from the text input (split by newlines)
2. Create a separate record for each intervention
3. All records will be stored successfully in the existing table

**No migration needed - the table is already correctly set up!**

