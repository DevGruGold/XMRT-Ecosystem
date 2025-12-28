import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface HealthMetric {
  timestamp: string
  service: string
  status: 'healthy' | 'degraded' | 'down'
  response_time_ms: number
  error_count: number
  restart_count: number
  details: Record<string, any>
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const startTime = Date.now()
    
    // Check auth service health
    const authHealth = await checkAuthHealth(supabaseClient)
    const responseTime = Date.now() - startTime
    
    // Detect crash loops
    const crashLoopDetected = await detectCrashLoop(supabaseClient)
    
    // Log health metric
    const metric: HealthMetric = {
      timestamp: new Date().toISOString(),
      service: 'gotrue-auth',
      status: crashLoopDetected ? 'degraded' : authHealth.status,
      response_time_ms: responseTime,
      error_count: authHealth.error_count,
      restart_count: authHealth.restart_count,
      details: {
        crash_loop_detected: crashLoopDetected,
        last_restart: authHealth.last_restart,
        consecutive_restarts: authHealth.consecutive_restarts,
        db_connections: authHealth.db_connections
      }
    }
    
    await supabaseClient
      .from('ecosystem_health_metrics')
      .insert({
        repo_name: 'suite',
        metric_type: 'auth_health',
        metric_value: responseTime,
        status: metric.status,
        details: metric.details
      })
    
    // Alert if crash loop detected
    if (crashLoopDetected) {
      await alertCrashLoop(supabaseClient, metric)
    }
    
    return new Response(
      JSON.stringify(metric),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )
  } catch (error) {
    console.error('Health check error:', error)
    
    return new Response(
      JSON.stringify({ 
        error: error.message,
        status: 'down',
        timestamp: new Date().toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})

async function checkAuthHealth(supabase: any) {
  try {
    // Query recent auth logs for errors and restarts
    const { data: logs, error } = await supabase
      .from('edge_function_logs')
      .select('*')
      .eq('level', 'error')
      .gte('timestamp', new Date(Date.now() - 5 * 60 * 1000).toISOString())
      .order('timestamp', { ascending: false })
      .limit(100)
    
    if (error) throw error
    
    // Count errors and restarts
    const errorCount = logs?.filter(l => l.error && l.error !== 'context canceled').length || 0
    const restartCount = logs?.filter(l => 
      l.msg?.includes('graceful shutdown') || 
      l.msg?.includes('exiting')
    ).length || 0
    
    // Detect consecutive restarts (crash loop indicator)
    const recentLogs = logs?.slice(0, 20) || []
    const consecutiveRestarts = recentLogs.filter(l => 
      l.msg?.includes('graceful shutdown')
    ).length
    
    const lastRestart = logs?.find(l => l.msg?.includes('graceful shutdown'))?.timestamp
    
    // Check DB connection health
    const { data: dbHealth } = await supabase.rpc('pg_stat_database')
    
    return {
      status: consecutiveRestarts > 3 ? 'degraded' : (errorCount > 10 ? 'degraded' : 'healthy'),
      error_count: errorCount,
      restart_count: restartCount,
      consecutive_restarts: consecutiveRestarts,
      last_restart: lastRestart,
      db_connections: dbHealth?.numbackends || 0
    }
  } catch (error) {
    console.error('Auth health check failed:', error)
    return {
      status: 'down',
      error_count: 1,
      restart_count: 0,
      consecutive_restarts: 0,
      last_restart: null,
      db_connections: 0
    }
  }
}

async function detectCrashLoop(supabase: any): Promise<boolean> {
  try {
    // Check for restarts in last 10 minutes
    const { data: restarts } = await supabase
      .from('edge_function_logs')
      .select('timestamp, msg')
      .ilike('msg', '%graceful shutdown%')
      .gte('timestamp', new Date(Date.now() - 10 * 60 * 1000).toISOString())
      .order('timestamp', { ascending: false })
    
    // Crash loop = 3+ restarts in 10 minutes
    return (restarts?.length || 0) >= 3
  } catch {
    return false
  }
}

async function alertCrashLoop(supabase: any, metric: HealthMetric) {
  try {
    // Insert alert to ecosystem_event_log
    await supabase.from('ecosystem_event_log').insert({
      event_type: 'crash_loop_detected',
      source_repo: 'suite',
      priority: 10, // Critical
      event_data: {
        metric: metric,
        alert_message: `Auth service crash loop detected: ${metric.details.consecutive_restarts} restarts in 10 minutes`,
        recommended_action: 'Check for memory leaks, database connection issues, or configuration errors'
      }
    })
    
    console.error('🚨 CRASH LOOP ALERT:', metric)
  } catch (error) {
    console.error('Failed to send crash loop alert:', error)
  }
}
