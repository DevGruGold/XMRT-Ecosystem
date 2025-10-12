-- XMRT Ecosystem Supabase Schema Fix
-- Addresses error: "Could not find the 'content' column of 'chat_messages' in the schema cache"

-- Drop and recreate table with correct schema
DROP TABLE IF EXISTS chat_messages CASCADE;

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,                    -- Required column that was missing
    message TEXT,                             -- Alternative message field
    sender TEXT NOT NULL,
    recipient TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    type TEXT DEFAULT 'user_chat',
    thread_id UUID,
    agent_id TEXT,
    session_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX idx_chat_messages_type ON chat_messages(type);
CREATE INDEX idx_chat_messages_sender ON chat_messages(sender);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_thread ON chat_messages(thread_id);

-- Enable Row Level Security
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create policies for access control
CREATE POLICY "Enable read access for all users" ON chat_messages
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for all users" ON chat_messages 
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for all users" ON chat_messages
    FOR UPDATE USING (true);

-- Create activity feed table if it doesn't exist
CREATE TABLE IF NOT EXISTS activity_feed (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    data JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for activity feed
CREATE INDEX IF NOT EXISTS idx_activity_feed_timestamp ON activity_feed(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_feed_type ON activity_feed(type);

-- Enable RLS for activity feed
ALTER TABLE activity_feed ENABLE ROW LEVEL SECURITY;

-- Activity feed policies
CREATE POLICY "Enable read access for activity feed" ON activity_feed
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for activity feed" ON activity_feed
    FOR INSERT WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE chat_messages IS 'Chat messages table for XMRT Ecosystem with proper content column';
COMMENT ON COLUMN chat_messages.content IS 'Main message content - fixes schema cache error';
COMMENT ON COLUMN chat_messages.message IS 'Alternative message field for compatibility';
COMMENT ON TABLE activity_feed IS 'Activity feed for XMRT Ecosystem agent discussions and events';

-- Insert test data to verify schema
INSERT INTO chat_messages (content, sender, type) 
VALUES ('Schema fix test message', 'system', 'system_test');

-- Clean up test data
DELETE FROM chat_messages WHERE content = 'Schema fix test message' AND sender = 'system';

-- Verification query
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
ORDER BY ordinal_position;
