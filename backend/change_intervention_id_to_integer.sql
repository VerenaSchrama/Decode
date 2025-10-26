-- Change intervention_id from UUID to INTEGER to align with InterventionsBASE.Intervention_ID
-- This allows proper foreign key relationships and data integrity

-- First, drop the existing column if it exists (to avoid conflicts)
ALTER TABLE public.intervention_periods 
DROP COLUMN IF EXISTS intervention_id;

-- Add intervention_id as INTEGER
ALTER TABLE public.intervention_periods
ADD COLUMN intervention_id INTEGER;

-- Add comment for documentation
COMMENT ON COLUMN public.intervention_periods.intervention_id IS 'Foreign key reference to InterventionsBASE.Intervention_ID (integer)';

-- Refresh the PostgREST schema cache so it recognizes the column type change
NOTIFY pgrst, 'reload schema';

-- Verify the change
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'intervention_periods' 
AND column_name = 'intervention_id';

