-- Intervention Periods Table
-- Tracks when users start interventions and their completion status

CREATE TABLE IF NOT EXISTS intervention_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL REFERENCES user_profiles(user_uuid) ON DELETE CASCADE,
    intake_id UUID NOT NULL REFERENCES intakes(id) ON DELETE CASCADE,
    intervention_name VARCHAR(255) NOT NULL,
    intervention_id VARCHAR(255), -- Reference to InterventionsBASE.Intervention_ID
    selected_habits TEXT[] DEFAULT '{}', -- Array of selected habit names
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    planned_end_date TIMESTAMP WITH TIME ZONE,
    actual_end_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'abandoned')),
    cycle_phase_at_start VARCHAR(50), -- Cycle phase when intervention started
    completion_percentage DECIMAL(5,2) DEFAULT 0.0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_intervention_periods_user_uuid ON intervention_periods(user_uuid);
CREATE INDEX IF NOT EXISTS idx_intervention_periods_status ON intervention_periods(status);
CREATE INDEX IF NOT EXISTS idx_intervention_periods_start_date ON intervention_periods(start_date);
CREATE INDEX IF NOT EXISTS idx_intervention_periods_intake_id ON intervention_periods(intake_id);

-- RLS Policies
ALTER TABLE intervention_periods ENABLE ROW LEVEL SECURITY;

-- Users can only see their own intervention periods
CREATE POLICY "Users can view their own intervention periods" ON intervention_periods
    FOR SELECT USING (auth.uid()::text = user_uuid::text);

-- Users can insert their own intervention periods
CREATE POLICY "Users can insert their own intervention periods" ON intervention_periods
    FOR INSERT WITH CHECK (auth.uid()::text = user_uuid::text);

-- Users can update their own intervention periods
CREATE POLICY "Users can update their own intervention periods" ON intervention_periods
    FOR UPDATE USING (auth.uid()::text = user_uuid::text);

-- Service role can do everything (for backend operations)
CREATE POLICY "Service role can manage all intervention periods" ON intervention_periods
    FOR ALL USING (auth.role() = 'service_role');

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_intervention_periods_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER trigger_update_intervention_periods_updated_at
    BEFORE UPDATE ON intervention_periods
    FOR EACH ROW
    EXECUTE FUNCTION update_intervention_periods_updated_at();

-- Add comments for documentation
COMMENT ON TABLE intervention_periods IS 'Tracks intervention periods for users, including start/end dates and completion status';
COMMENT ON COLUMN intervention_periods.user_uuid IS 'Reference to user_profiles table';
COMMENT ON COLUMN intervention_periods.intake_id IS 'Reference to the intake that generated this intervention';
COMMENT ON COLUMN intervention_periods.intervention_name IS 'Name of the intervention (e.g., "Control your blood sugar")';
COMMENT ON COLUMN intervention_periods.intervention_id IS 'ID from InterventionsBASE table if available';
COMMENT ON COLUMN intervention_periods.selected_habits IS 'Array of habit names selected by the user';
COMMENT ON COLUMN intervention_periods.status IS 'Current status: active, completed, paused, abandoned';
COMMENT ON COLUMN intervention_periods.completion_percentage IS 'Overall completion percentage (0-100)';
COMMENT ON COLUMN intervention_periods.cycle_phase_at_start IS 'Menstrual cycle phase when intervention started';
