"""
Supabase client for XMRT-Ecosystem
Connects to shared Supabase instance with xmrtcouncil
"""
from supabase import create_client, Client
import os
from typing import Optional
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vawouugtzwmejxqkeqqj.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client singleton"""
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_KEY:
            raise ValueError("SUPABASE_ANON_KEY environment variable not set")
        
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL}")
    
    return _supabase_client

def log_activity(
    activity_type: str,
    title: str,
    description: str = "",
    metadata: dict = None,
    status: str = "completed"
):
    """
    Log activity to eliza_activity_log table
    
    Args:
        activity_type: Type of activity (e.g., 'agent_coordination', 'github_action')
        title: Short title of the activity
        description: Detailed description
        metadata: Additional JSON metadata
        status: Activity status ('in_progress', 'completed', 'failed')
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "activity_type": activity_type,
            "title": title,
            "description": description,
            "metadata": metadata or {},
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("eliza_activity_log").insert(data).execute()
        print(f"✅ Logged activity: {title}")
        return response.data
        
    except Exception as e:
        print(f"⚠️ Failed to log activity: {str(e)}")
        return None

def register_agent(
    agent_name: str,
    display_name: str,
    edge_function_name: str,
    description: str = "",
    category: str = "ecosystem_coordinator",
    priority: int = 5
):
    """
    Register agent in superduper_agents table
    
    Args:
        agent_name: Unique agent identifier
        display_name: Human-readable name
        edge_function_name: API endpoint or function name
        description: What the agent does
        category: Agent category
        priority: Priority level (1-10)
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "agent_name": agent_name,
            "display_name": display_name,
            "edge_function_name": edge_function_name,
            "description": description,
            "category": category,
            "priority": priority,
            "status": "active",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Upsert to avoid duplicates
        response = supabase.table("superduper_agents").upsert(
            data,
            on_conflict="agent_name"
        ).execute()
        
        print(f"✅ Registered agent: {display_name}")
        return response.data
        
    except Exception as e:
        print(f"⚠️ Failed to register agent: {str(e)}")
        return None

def get_registered_agents(status: str = "active"):
    """
    Get all registered agents from superduper_agents table
    
    Args:
        status: Filter by status ('active', 'inactive', etc.)
    
    Returns:
        List of agent records
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("superduper_agents").select("*")
        
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        print(f"✅ Retrieved {len(response.data)} agents")
        return response.data
        
    except Exception as e:
        print(f"⚠️ Failed to get agents: {str(e)}")
        return []

def update_agent_metrics(
    agent_name: str,
    execution_count: int = None,
    success_count: int = None,
    failure_count: int = None
):
    """
    Update agent performance metrics
    
    Args:
        agent_name: Agent to update
        execution_count: Total executions
        success_count: Successful executions
        failure_count: Failed executions
    """
    try:
        supabase = get_supabase_client()
        
        data = {"updated_at": datetime.utcnow().isoformat()}
        
        if execution_count is not None:
            data["execution_count"] = execution_count
        if success_count is not None:
            data["success_count"] = success_count
        if failure_count is not None:
            data["failure_count"] = failure_count
        
        response = supabase.table("superduper_agents").update(data).eq(
            "agent_name", agent_name
        ).execute()
        
        print(f"✅ Updated metrics for: {agent_name}")
        return response.data
        
    except Exception as e:
        print(f"⚠️ Failed to update metrics: {str(e)}")
        return None
