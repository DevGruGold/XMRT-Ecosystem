-- OPTIONAL HARDENING for XMRT Ecosystem Supabase Schema
-- Run this AFTER the main fix and AFTER you've verified everything works
-- Only run if you say "enforce payload"

-- 1. Add CHECK constraint to ensure at least one of content or message is provided
ALTER TABLE chat_messages 
ADD CONSTRAINT check_content_or_message 
CHECK (content IS NOT NULL OR message IS NOT NULL);

-- 2. Add NOT NULL constraint on content (only after fully migrated off message field)
-- UNCOMMENT ONLY when you're sure all code uses 'content' field:
-- ALTER TABLE chat_messages ALTER COLUMN content SET NOT NULL;

-- 3. Add enum constraint for sender/role with strict values
-- Create enum type for sender values
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sender_type') THEN
        CREATE TYPE sender_type AS ENUM ('User', 'System', 'Agent', 'AI', 'Bot', 'Admin', 'Service');
    END IF;
END $$;

-- Add sender enum constraint (this will validate all existing data first)
-- UNCOMMENT if you want strict sender validation:
-- ALTER TABLE chat_messages ALTER COLUMN sender TYPE sender_type USING sender::sender_type;

-- 4. Add enum constraint for message types
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_type') THEN
        CREATE TYPE message_type AS ENUM (
            'user_chat', 
            'system', 
            'agent_discussion', 
            'notification', 
            'error', 
            'debug', 
            'status_update',
            'system_test'
        );
    END IF;
END $$;

-- Add type enum constraint
-- UNCOMMENT if you want strict type validation:
-- ALTER TABLE chat_messages ALTER COLUMN type TYPE message_type USING type::message_type;

-- 5. Add additional validation constraints
ALTER TABLE chat_messages 
ADD CONSTRAINT check_sender_not_empty 
CHECK (length(trim(sender)) > 0);

ALTER TABLE chat_messages 
ADD CONSTRAINT check_content_not_empty 
CHECK (content IS NULL OR length(trim(content)) > 0);

-- 6. Add updated_at trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_chat_messages_updated_at
    BEFORE UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7. Add row-level validation function
CREATE OR REPLACE FUNCTION validate_chat_message()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure sender is provided
    IF NEW.sender IS NULL OR length(trim(NEW.sender)) = 0 THEN
        RAISE EXCEPTION 'sender is required and cannot be empty';
    END IF;
    
    -- Ensure at least content or message is provided
    IF (NEW.content IS NULL OR length(trim(NEW.content)) = 0) AND 
       (NEW.message IS NULL OR length(trim(NEW.message)) = 0) THEN
        RAISE EXCEPTION 'Either content or message must be provided and non-empty';
    END IF;
    
    -- Ensure type is provided
    IF NEW.type IS NULL OR length(trim(NEW.type)) = 0 THEN
        NEW.type := 'user_chat';  -- Default fallback
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add validation trigger
DROP TRIGGER IF EXISTS trigger_validate_chat_message ON chat_messages;
CREATE TRIGGER trigger_validate_chat_message
    BEFORE INSERT OR UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION validate_chat_message();

-- Test hardened schema with valid data
INSERT INTO chat_messages (sender, content, type) 
VALUES ('User', 'Hardening test message', 'user_chat');

-- Test that invalid data is rejected
-- These should fail:
-- INSERT INTO chat_messages (content, type) VALUES ('No sender', 'user_chat');  -- Should fail: no sender
-- INSERT INTO chat_messages (sender, type) VALUES ('User', 'user_chat');        -- Should fail: no content or message
-- INSERT INTO chat_messages (sender, content) VALUES ('', 'Empty sender');      -- Should fail: empty sender

-- Clean up test
DELETE FROM chat_messages WHERE content = 'Hardening test message';

-- Display final schema with constraints
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
ORDER BY ordinal_position;

-- Display constraints
SELECT 
    constraint_name,
    constraint_type,
    check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name = 'chat_messages'
ORDER BY constraint_type, constraint_name;