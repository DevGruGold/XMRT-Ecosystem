-- Migration: Enhanced Auth Event Logging
-- Prevents crash loops by adding proper auth event tracking

-- Create auth_service_logs table
CREATE TABLE IF NOT EXISTS auth_service_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    error_details JSONB,
    component TEXT,
    user_id TEXT,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_auth_logs_event ON auth_service_logs(event_type);
CREATE INDEX idx_auth_logs_level ON auth_service_logs(level);
CREATE INDEX idx_auth_logs_created ON auth_service_logs(created_at DESC);
CREATE INDEX idx_auth_logs_user ON auth_service_logs(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_auth_logs_error ON auth_service_logs(level) WHERE level IN ('error', 'critical');

-- Create restart tracking table
CREATE TABLE IF NOT EXISTS auth_service_restarts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restart_reason TEXT,
    error_count INTEGER DEFAULT 0,
    logs_before_restart JSONB,
    uptime_seconds INTEGER,
    memory_mb INTEGER,
    cpu_percent NUMERIC(5,2),
    db_connections INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index
CREATE INDEX idx_auth_restarts_created ON auth_service_restarts(created_at DESC);

-- Function to detect crash loops
CREATE OR REPLACE FUNCTION detect_auth_crash_loop()
RETURNS TABLE (
    is_crash_loop BOOLEAN,
    restart_count INTEGER,
    time_window_minutes INTEGER,
    last_restart TIMESTAMPTZ,
    avg_uptime_seconds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) >= 3 as is_crash_loop,
        COUNT(*)::INTEGER as restart_count,
        10 as time_window_minutes,
        MAX(created_at) as last_restart,
        AVG(uptime_seconds)::NUMERIC as avg_uptime_seconds
    FROM auth_service_restarts
    WHERE created_at > NOW() - INTERVAL '10 minutes';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log auth errors with context
CREATE OR REPLACE FUNCTION log_auth_error(
    p_event_type TEXT,
    p_message TEXT,
    p_error_details JSONB DEFAULT NULL,
    p_component TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO auth_service_logs (
        event_type,
        level,
        message,
        error_details,
        component,
        metadata
    )
    VALUES (
        p_event_type,
        'error',
        p_message,
        p_error_details,
        p_component,
        p_metadata
    )
    RETURNING id INTO v_log_id;
    
    -- Alert if this is a critical error
    IF p_event_type IN ('crash', 'fatal_error', 'panic') THEN
        INSERT INTO ecosystem_event_log (event_type, source_repo, event_data, priority)
        VALUES (
            'auth_critical_error',
            'suite',
            jsonb_build_object(
                'log_id', v_log_id,
                'error', p_message,
                'component', p_component
            ),
            10
        );
    END IF;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comments
COMMENT ON TABLE auth_service_logs IS 'Detailed auth service event logs with error tracking';
COMMENT ON TABLE auth_service_restarts IS 'Tracks auth service restarts to detect crash loops';
COMMENT ON FUNCTION detect_auth_crash_loop IS 'Detects if auth service is in a crash loop';
