-- XMRT Ecosystem Supabase Schema Fix - Updated with Exact Requirements
-- Addresses error: "Could not find the 'content' column of 'chat_messages' in the schema cache"
-- Based on actual API requirements: sender, content, and type are required

-- First, let's check if the table exists and what columns it has
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'chat_messages') THEN
        RAISE NOTICE 'Table chat_messages exists, checking schema...';
    ELSE
        RAISE NOTICE 'Table chat_messages does not exist, will create it...';
    END IF;
END $$;

-- Add the missing content column if it doesn't exist
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS content TEXT;

-- Ensure sender column exists and is properly configured
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS sender TEXT;
ALTER TABLE chat_messages ALTER COLUMN sender SET NOT NULL;

-- Ensure type column exists with default
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'user_chat';

-- Create a trigger to copy message to content if content is missing
-- This provides backward compatibility for existing code using 'message' field
CREATE OR REPLACE FUNCTION sync_message_content()
RETURNS TRIGGER AS $$
BEGIN
    -- If content is null but message exists, copy message to content
    IF NEW.content IS NULL AND NEW.message IS NOT NULL THEN
        NEW.content := NEW.message;
    END IF;
    
    -- If message is null but content exists, copy content to message
    IF NEW.message IS NULL AND NEW.content IS NOT NULL THEN
        NEW.message := NEW.content;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for INSERT and UPDATE
DROP TRIGGER IF EXISTS trigger_sync_message_content ON chat_messages;
CREATE TRIGGER trigger_sync_message_content
    BEFORE INSERT OR UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION sync_message_content();

-- Add other useful columns if they don't exist
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS session_id TEXT;
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS thread_id UUID;
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_messages_type ON chat_messages(type);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON chat_messages(sender);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

-- Enable Row Level Security if not already enabled
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create policies (replace existing ones)
DROP POLICY IF EXISTS "Enable read access for all users" ON chat_messages;
DROP POLICY IF EXISTS "Enable insert for all users" ON chat_messages;
DROP POLICY IF EXISTS "Enable update for all users" ON chat_messages;

CREATE POLICY "Enable read access for all users" ON chat_messages
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for all users" ON chat_messages 
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for all users" ON chat_messages
    FOR UPDATE USING (true);

-- Test the fix with the exact minimal JSON requirements
INSERT INTO chat_messages (sender, content, type) 
VALUES ('User', 'Hello world!', 'user_chat');

-- Test backward compatibility with message field
INSERT INTO chat_messages (sender, message, type) 
VALUES ('System', 'Test message compatibility', 'system');

-- Verify both inserts worked and trigger copied data correctly
SELECT id, sender, content, message, type, timestamp 
FROM chat_messages 
WHERE content IN ('Hello world!', 'Test message compatibility')
ORDER BY timestamp DESC;

-- Clean up test data
DELETE FROM chat_messages WHERE content IN ('Hello world!', 'Test message compatibility');

-- Display current schema
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
ORDER BY ordinal_position;

-- Comments for documentation
COMMENT ON TABLE chat_messages IS 'Chat messages table for XMRT Ecosystem - fixed with required content column';
COMMENT ON COLUMN chat_messages.content IS 'Message content - required field that was missing';
COMMENT ON COLUMN chat_messages.sender IS 'Message sender - required field (User, System, Agent, etc.)';
COMMENT ON COLUMN chat_messages.type IS 'Message type - defaults to user_chat';
COMMENT ON FUNCTION sync_message_content() IS 'Trigger function to sync content and message fields for backward compatibility';