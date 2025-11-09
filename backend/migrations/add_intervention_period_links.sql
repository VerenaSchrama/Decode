-- Migration: Add intervention_period_id foreign keys and planned_duration_days column
-- This migration adds proper linking between intervention periods and daily progress entries

-- ============================================================================
-- 1. Add planned_duration_days column to intervention_periods table
-- ============================================================================

-- Check if column already exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'intervention_periods' 
        AND column_name = 'planned_duration_days'
    ) THEN
        ALTER TABLE public.intervention_periods 
        ADD COLUMN planned_duration_days INTEGER;
        
        -- Calculate planned_duration_days from existing start_date and end_date
        -- for records that don't have it set
        UPDATE public.intervention_periods
        SET planned_duration_days = (
            EXTRACT(EPOCH FROM (end_date::date - start_date::date)) / 86400 + 1
        )::INTEGER
        WHERE planned_duration_days IS NULL 
        AND end_date IS NOT NULL 
        AND start_date IS NOT NULL;
        
        -- Set default for any remaining NULL values
        UPDATE public.intervention_periods
        SET planned_duration_days = 30
        WHERE planned_duration_days IS NULL;
        
        -- Add comment
        COMMENT ON COLUMN public.intervention_periods.planned_duration_days IS 
            'Planned duration of the intervention period in days';
    END IF;
END $$;

-- ============================================================================
-- 2. Add intervention_period_id to daily_habit_entries table
-- ============================================================================

-- Add column (nullable to allow existing data)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'daily_habit_entries' 
        AND column_name = 'intervention_period_id'
    ) THEN
        ALTER TABLE public.daily_habit_entries 
        ADD COLUMN intervention_period_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE public.daily_habit_entries
        ADD CONSTRAINT fk_daily_habit_entries_intervention_period
        FOREIGN KEY (intervention_period_id) 
        REFERENCES public.intervention_periods(id) 
        ON DELETE SET NULL;
        
        -- Add index for faster lookups
        CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_intervention_period_id 
        ON public.daily_habit_entries(intervention_period_id);
        
        -- Add comment
        COMMENT ON COLUMN public.daily_habit_entries.intervention_period_id IS 
            'Foreign key to intervention_periods table. Links habit entries to specific intervention periods.';
    END IF;
END $$;

-- ============================================================================
-- 3. Add intervention_period_id to daily_summaries table
-- ============================================================================

-- Add column (nullable to allow existing data)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'daily_summaries' 
        AND column_name = 'intervention_period_id'
    ) THEN
        ALTER TABLE public.daily_summaries 
        ADD COLUMN intervention_period_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE public.daily_summaries
        ADD CONSTRAINT fk_daily_summaries_intervention_period
        FOREIGN KEY (intervention_period_id) 
        REFERENCES public.intervention_periods(id) 
        ON DELETE SET NULL;
        
        -- Add index for faster lookups
        CREATE INDEX IF NOT EXISTS idx_daily_summaries_intervention_period_id 
        ON public.daily_summaries(intervention_period_id);
        
        -- Add comment
        COMMENT ON COLUMN public.daily_summaries.intervention_period_id IS 
            'Foreign key to intervention_periods table. Links daily summaries to specific intervention periods.';
    END IF;
END $$;

-- ============================================================================
-- 4. Add intervention_period_id to daily_moods table
-- ============================================================================

-- Add column (nullable to allow existing data)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'daily_moods' 
        AND column_name = 'intervention_period_id'
    ) THEN
        ALTER TABLE public.daily_moods 
        ADD COLUMN intervention_period_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE public.daily_moods
        ADD CONSTRAINT fk_daily_moods_intervention_period
        FOREIGN KEY (intervention_period_id) 
        REFERENCES public.intervention_periods(id) 
        ON DELETE SET NULL;
        
        -- Add index for faster lookups
        CREATE INDEX IF NOT EXISTS idx_daily_moods_intervention_period_id 
        ON public.daily_moods(intervention_period_id);
        
        -- Add comment
        COMMENT ON COLUMN public.daily_moods.intervention_period_id IS 
            'Foreign key to intervention_periods table. Links mood entries to specific intervention periods.';
    END IF;
END $$;

-- ============================================================================
-- 5. Fix or drop outdated trigger functions that reference removed columns
-- ============================================================================
-- Some trigger functions may reference the old 'mood' column in daily_habit_entries
-- which was moved to daily_moods table. We need to drop or update these triggers.

-- Drop all triggers that depend on the update_daily_summary function
DROP TRIGGER IF EXISTS trigger_update_daily_summary_insert ON public.daily_habit_entries;
DROP TRIGGER IF EXISTS trigger_update_daily_summary_update ON public.daily_habit_entries;
DROP TRIGGER IF EXISTS trigger_update_daily_summary_delete ON public.daily_habit_entries;
DROP TRIGGER IF EXISTS trigger_update_daily_summary ON public.daily_habit_entries;

-- Now drop the function (it references the removed mood column)
DROP FUNCTION IF EXISTS public.update_daily_summary();

-- Note: If you need a similar trigger in the future, it should reference
-- the daily_moods table instead of daily_habit_entries for mood data.

-- ============================================================================
-- 6. Optional: Backfill intervention_period_id for existing data
-- ============================================================================
-- This script attempts to link existing entries to intervention periods
-- based on date ranges. Run this AFTER the columns are added.

-- Backfill daily_habit_entries
UPDATE public.daily_habit_entries dhe
SET intervention_period_id = ip.id
FROM public.intervention_periods ip
WHERE dhe.intervention_period_id IS NULL
  AND dhe.user_id = ip.user_id
  AND dhe.entry_date::date >= ip.start_date::date
  AND (ip.end_date IS NULL OR dhe.entry_date::date <= ip.end_date::date)
  AND ip.status = 'active'
  AND NOT EXISTS (
    -- Avoid duplicates: if multiple periods overlap, prefer the most recent one
    SELECT 1 
    FROM public.intervention_periods ip2
    WHERE ip2.user_id = ip.user_id
      AND ip2.start_date::date <= dhe.entry_date::date
      AND (ip2.end_date IS NULL OR ip2.end_date::date >= dhe.entry_date::date)
      AND ip2.status = 'active'
      AND ip2.created_at > ip.created_at
  );

-- Backfill daily_summaries
UPDATE public.daily_summaries ds
SET intervention_period_id = ip.id
FROM public.intervention_periods ip
WHERE ds.intervention_period_id IS NULL
  AND ds.user_id = ip.user_id
  AND ds.entry_date::date >= ip.start_date::date
  AND (ip.end_date IS NULL OR ds.entry_date::date <= ip.end_date::date)
  AND ip.status = 'active'
  AND NOT EXISTS (
    SELECT 1 
    FROM public.intervention_periods ip2
    WHERE ip2.user_id = ip.user_id
      AND ip2.start_date::date <= ds.entry_date::date
      AND (ip2.end_date IS NULL OR ip2.end_date::date >= ds.entry_date::date)
      AND ip2.status = 'active'
      AND ip2.created_at > ip.created_at
  );

-- Backfill daily_moods
UPDATE public.daily_moods dm
SET intervention_period_id = ip.id
FROM public.intervention_periods ip
WHERE dm.intervention_period_id IS NULL
  AND dm.user_id = ip.user_id
  AND dm.entry_date::date >= ip.start_date::date
  AND (ip.end_date IS NULL OR dm.entry_date::date <= ip.end_date::date)
  AND ip.status = 'active'
  AND NOT EXISTS (
    SELECT 1 
    FROM public.intervention_periods ip2
    WHERE ip2.user_id = ip.user_id
      AND ip2.start_date::date <= dm.entry_date::date
      AND (ip2.end_date IS NULL OR ip2.end_date::date >= dm.entry_date::date)
      AND ip2.status = 'active'
      AND ip2.created_at > ip.created_at
  );

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Summary:
-- 1. Added planned_duration_days column to intervention_periods
-- 2. Added intervention_period_id foreign keys to:
--    - daily_habit_entries
--    - daily_summaries
--    - daily_moods
-- 3. Created indexes for performance
-- 4. Fixed/dropped outdated trigger functions that referenced removed mood column
-- 5. Backfilled existing data where possible
--
-- Note: New entries should populate intervention_period_id when created.
-- Update the backend API endpoints to set this field when saving daily progress.

