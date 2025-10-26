-- Add missing columns to intervention_periods table
-- These columns are needed to align with the backend and frontend models

ALTER TABLE public.intervention_periods
ADD COLUMN IF NOT EXISTS intervention_name VARCHAR(255);

ALTER TABLE public.intervention_periods
ADD COLUMN IF NOT EXISTS selected_habits JSONB;

ALTER TABLE public.intervention_periods
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Rename end_date to planned_end_date to match backend code
-- (The backend uses 'planned_end_date' but the table has 'end_date')
-- Since 'end_date' already exists, we'll keep it and update the backend code

-- If cycle_phase column doesn't exist or was removed, add it back
ALTER TABLE public.intervention_periods
ADD COLUMN IF NOT EXISTS cycle_phase VARCHAR(50);

-- Add comments for documentation
COMMENT ON COLUMN public.intervention_periods.intervention_name IS 'Name of the intervention strategy';
COMMENT ON COLUMN public.intervention_periods.selected_habits IS 'JSONB array of habit names selected by the user';
COMMENT ON COLUMN public.intervention_periods.notes IS 'User notes about the intervention period';
COMMENT ON COLUMN public.intervention_periods.cycle_phase IS 'Menstrual cycle phase when the intervention period started';

-- Refresh the PostgREST schema cache so it recognizes the new columns
NOTIFY pgrst, 'reload schema';

