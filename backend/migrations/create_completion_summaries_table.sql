-- Migration: Create completion_summaries table
-- Stores analytics summaries when intervention periods are completed

CREATE TABLE IF NOT EXISTS completion_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intervention_period_id UUID NOT NULL REFERENCES intervention_periods(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    adherence_rate DECIMAL(5, 2) NOT NULL,  -- Percentage (0-100)
    average_mood DECIMAL(3, 2),  -- Average mood score (1-5)
    mood_trend TEXT CHECK (mood_trend IN ('improved', 'declined', 'stable')),
    summary_json JSONB,  -- Additional structured insights
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_completion_summaries_period_id ON completion_summaries(intervention_period_id);
CREATE INDEX IF NOT EXISTS idx_completion_summaries_user_id ON completion_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_completion_summaries_created_at ON completion_summaries(created_at DESC);

-- Add RLS policies (if using RLS)
-- ALTER TABLE completion_summaries ENABLE ROW LEVEL SECURITY;
-- 
-- CREATE POLICY "Users can view their own completion summaries"
--     ON completion_summaries FOR SELECT
--     USING (auth.uid() = user_id);
-- 
-- CREATE POLICY "Service role can insert completion summaries"
--     ON completion_summaries FOR INSERT
--     WITH CHECK (true);

COMMENT ON TABLE completion_summaries IS 'Analytics summaries generated when intervention periods are completed';
COMMENT ON COLUMN completion_summaries.adherence_rate IS 'Percentage of habit adherence (0-100)';
COMMENT ON COLUMN completion_summaries.average_mood IS 'Average mood score during intervention period (1-5)';
COMMENT ON COLUMN completion_summaries.mood_trend IS 'Trend direction: improved, declined, or stable';
COMMENT ON COLUMN completion_summaries.summary_json IS 'Additional structured insights (streaks, missed days, etc.)';

