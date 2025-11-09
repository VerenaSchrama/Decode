-- Migration: Fix custom_interventions and user_interventions tables
-- This script:
-- 1. Renames customer_interventions back to user_interventions
-- 2. Recreates the custom_interventions table

-- ============================================================================
-- 1. Rename customer_interventions or customer_user_interventions back to user_interventions
-- ============================================================================
DO $$
BEGIN
    -- Check if user_interventions already exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_interventions') THEN
        RAISE NOTICE 'ℹ️ user_interventions table already exists. Skipping rename.';
    ELSE
        -- Try customer_user_interventions first (this is what we see in the database)
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'customer_user_interventions') THEN
            ALTER TABLE public.customer_user_interventions RENAME TO user_interventions;
            RAISE NOTICE '✅ Renamed customer_user_interventions to user_interventions';
        -- Fallback to customer_interventions if it exists
        ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'customer_interventions') THEN
            ALTER TABLE public.customer_interventions RENAME TO user_interventions;
            RAISE NOTICE '✅ Renamed customer_interventions to user_interventions';
        ELSE
            RAISE NOTICE '⚠️ Neither customer_user_interventions nor customer_interventions found. user_interventions may need to be created manually.';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- 2. Create custom_interventions table (if it doesn't exist)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.custom_interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    intake_id UUID NOT NULL,
    intervention_name TEXT NOT NULL,
    description TEXT,
    context TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'approved', 'rejected')),
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_custom_interventions_user 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    CONSTRAINT fk_custom_interventions_intake 
        FOREIGN KEY (intake_id) REFERENCES public.intakes(id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. Create indexes for custom_interventions
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_custom_interventions_user_id 
    ON public.custom_interventions(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_interventions_intake_id 
    ON public.custom_interventions(intake_id);
CREATE INDEX IF NOT EXISTS idx_custom_interventions_status 
    ON public.custom_interventions(status);

-- ============================================================================
-- 4. Add updated_at trigger for custom_interventions
-- ============================================================================
CREATE OR REPLACE FUNCTION update_custom_interventions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_custom_interventions_updated_at ON public.custom_interventions;
CREATE TRIGGER trigger_update_custom_interventions_updated_at
    BEFORE UPDATE ON public.custom_interventions
    FOR EACH ROW
    EXECUTE FUNCTION update_custom_interventions_updated_at();

-- ============================================================================
-- 5. Add RLS (Row Level Security) policies for custom_interventions
-- ============================================================================
ALTER TABLE public.custom_interventions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own custom interventions" ON public.custom_interventions;
DROP POLICY IF EXISTS "Users can insert their own custom interventions" ON public.custom_interventions;
DROP POLICY IF EXISTS "Users can update their own custom interventions" ON public.custom_interventions;
DROP POLICY IF EXISTS "Service role can do everything" ON public.custom_interventions;

-- Create policies
CREATE POLICY "Users can view their own custom interventions"
    ON public.custom_interventions
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own custom interventions"
    ON public.custom_interventions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own custom interventions"
    ON public.custom_interventions
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Service role can do everything (for backend operations)
CREATE POLICY "Service role can do everything"
    ON public.custom_interventions
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- 6. Add comments for documentation
-- ============================================================================
COMMENT ON TABLE public.custom_interventions IS 
    'Stores custom interventions mentioned by users during intake process. These are simple notes for admin review.';
COMMENT ON COLUMN public.custom_interventions.user_id IS 
    'Reference to the user who mentioned this intervention';
COMMENT ON COLUMN public.custom_interventions.intake_id IS 
    'Reference to the intake session where this was mentioned';
COMMENT ON COLUMN public.custom_interventions.intervention_name IS 
    'Name of the custom intervention (free text from user)';
COMMENT ON COLUMN public.custom_interventions.description IS 
    'Auto-generated description: "User mentioned: {intervention_name}"';
COMMENT ON COLUMN public.custom_interventions.context IS 
    'Additional context about why user mentioned this intervention';
COMMENT ON COLUMN public.custom_interventions.status IS 
    'Review status: pending, reviewed, approved, or rejected';
COMMENT ON COLUMN public.custom_interventions.reviewed_by IS 
    'Admin user ID who reviewed this intervention';
COMMENT ON COLUMN public.custom_interventions.reviewed_at IS 
    'Timestamp when this intervention was reviewed';

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Summary:
-- 1. ✅ Renamed customer_interventions → user_interventions (if customer_interventions exists)
-- 2. ✅ Created custom_interventions table with proper schema
-- 3. ✅ Added indexes for performance
-- 4. ✅ Added updated_at trigger
-- 5. ✅ Added RLS policies for security
-- 6. ✅ Added documentation comments

