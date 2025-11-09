-- Migration: Create notifications table
-- Stores in-app notifications for users

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- e.g., 'intervention_completed', 'milestone', etc.
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    data JSONB,  -- Additional notification data
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(user_id, read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- Add RLS policies (if using RLS)
-- ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
-- 
-- CREATE POLICY "Users can view their own notifications"
--     ON notifications FOR SELECT
--     USING (auth.uid() = user_id);
-- 
-- CREATE POLICY "Users can update their own notifications"
--     ON notifications FOR UPDATE
--     USING (auth.uid() = user_id);
-- 
-- CREATE POLICY "Service role can insert notifications"
--     ON notifications FOR INSERT
--     WITH CHECK (true);

COMMENT ON TABLE notifications IS 'In-app notifications for users';
COMMENT ON COLUMN notifications.type IS 'Notification type identifier';
COMMENT ON COLUMN notifications.data IS 'Additional notification payload (JSON)';

