-- Add missing actual_end_date column to intervention_periods table
-- This column tracks when users actually complete their interventions

ALTER TABLE intervention_periods 
ADD COLUMN actual_end_date TIMESTAMP WITH TIME ZONE;

-- Add a comment to document the column purpose
COMMENT ON COLUMN intervention_periods.actual_end_date IS 'Actual completion date when user finishes the intervention period';

-- Optional: Add an index for better query performance
CREATE INDEX IF NOT EXISTS idx_intervention_periods_actual_end_date 
ON intervention_periods(actual_end_date);
