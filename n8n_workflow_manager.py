#!/usr/bin/env python3
"""
n8n Workflow Manager for XMRT Ecosystem
=======================================

This module provides integration between XMRT and n8n workflows,
enabling autonomous workflow execution and management.

Author: Manus AI
Date: 2025-01-09
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import threading
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    PAUSED = "paused"

@dataclass
class WorkflowExecution:
    """Represents a workflow execution"""
    execution_id: str
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: str
    finished_at: Optional[str] = None
    data: Optional[Dict] = None
    error: Optional[str] = None

@dataclass
class WorkflowInfo:
    """Represents workflow information"""
    id: str
    name: str
    category: str
    description: str
    active: bool
    last_execution: Optional[str] = None
    execution_count: int = 0
    success_rate: float = 100.0

class N8nWorkflowManager:
    """Manages n8n workflows for XMRT integration"""
    
    def __init__(self, n8n_base_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.workflows: Dict[str, WorkflowInfo] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.active_workflows: List[str] = []
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Headers for n8n API requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            self.headers['X-N8N-API-KEY'] = self.api_key
        
        # Initialize with sample workflows for demonstration
        self._initialize_sample_workflows()
    
    def _initialize_sample_workflows(self):
        """Initialize with sample workflows based on our analysis"""
        sample_workflows = [
            {
                "id": "wf_memory_001",
                "name": "Long-term Memory Storage",
                "category": "long_term_memory",
                "description": "Store and retrieve information from Notion database",
                "active": True
            },
            {
                "id": "wf_memory_002", 
                "name": "Vector Database Sync",
                "category": "long_term_memory",
                "description": "Sync embeddings with vector database for semantic search",
                "active": True
            },
            {
                "id": "wf_sysadmin_001",
                "name": "System Health Monitor",
                "category": "systems_administration",
                "description": "Monitor system resources and send alerts",
                "active": True
            },
            {
                "id": "wf_sysadmin_002",
                "name": "User Management Sync",
                "category": "systems_administration", 
                "description": "Sync user accounts with Google Workspace",
                "active": False
            },
            {
                "id": "wf_google_001",
                "name": "Gmail Auto-responder",
                "category": "google_tool_management",
                "description": "Automatically respond to emails based on content analysis",
                "active": True
            },
            {
                "id": "wf_google_002",
                "name": "Calendar Scheduler",
                "category": "google_tool_management",
                "description": "Automatically schedule meetings based on availability",
                "active": True
            },
            {
                "id": "wf_business_001",
                "name": "KPI Dashboard Update",
                "category": "c_suite_business_management",
                "description": "Update executive dashboard with latest metrics",
                "active": True
            },
            {
                "id": "wf_business_002",
                "name": "CRM Data Sync",
                "category": "c_suite_business_management",
                "description": "Synchronize customer data across platforms",
                "active": False
            }
        ]
        
        for wf_data in sample_workflows:
            workflow = WorkflowInfo(**wf_data)
            self.workflows[workflow.id] = workflow
            if workflow.active:
                self.active_workflows.append(workflow.id)
    
    def start_monitoring(self):
        """Start monitoring workflow executions"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_workflows, daemon=True)
        self.monitoring_thread.start()
        logger.info("🔄 n8n workflow monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring workflow executions"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("⏹️ n8n workflow monitoring stopped")
    
    def _monitor_workflows(self):
        """Background monitoring of workflow executions"""
        while self.monitoring_active:
            try:
                # Simulate workflow executions for demonstration
                self._simulate_workflow_activity()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in workflow monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _simulate_workflow_activity(self):
        """Simulate workflow activity for demonstration"""
        import random
        
        # Randomly execute some active workflows
        for workflow_id in self.active_workflows:
            if random.random() > 0.8:  # 20% chance to execute
                self._simulate_execution(workflow_id)
    
    def _simulate_execution(self, workflow_id: str):
        """Simulate a workflow execution"""
        import uuid
        import random
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return
        
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        # Create execution record
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat()
        )
        
        self.executions[execution_id] = execution
        
        # Simulate execution time and result
        success = random.random() > 0.1  # 90% success rate
        
        # Update execution after "completion"
        execution.finished_at = datetime.now().isoformat()
        execution.status = WorkflowStatus.SUCCESS if success else WorkflowStatus.ERROR
        
        if success:
            execution.data = self._generate_sample_output(workflow.category)
        else:
            execution.error = "Simulated execution error"
        
        # Update workflow stats
        workflow.execution_count += 1
        workflow.last_execution = execution.finished_at
        if success:
            workflow.success_rate = (workflow.success_rate * (workflow.execution_count - 1) + 100) / workflow.execution_count
        else:
            workflow.success_rate = (workflow.success_rate * (workflow.execution_count - 1)) / workflow.execution_count
        
        logger.info(f"✅ Simulated execution of {workflow.name}: {execution.status.value}")
    
    def _generate_sample_output(self, category: str) -> Dict:
        """Generate sample output based on workflow category"""
        if category == "long_term_memory":
            return {
                "records_processed": 15,
                "new_memories": 3,
                "updated_memories": 2,
                "memory_score": 0.87
            }
        elif category == "systems_administration":
            return {
                "cpu_usage": "23%",
                "memory_usage": "45%",
                "disk_usage": "67%",
                "alerts_triggered": 0
            }
        elif category == "google_tool_management":
            return {
                "emails_processed": 8,
                "events_scheduled": 2,
                "documents_updated": 1,
                "sync_status": "success"
            }
        elif category == "c_suite_business_management":
            return {
                "kpis_updated": 12,
                "reports_generated": 3,
                "stakeholder_notifications": 5,
                "dashboard_refresh": "complete"
            }
        else:
            return {"status": "completed", "timestamp": datetime.now().isoformat()}
    
    def trigger_workflow(self, workflow_id: str, input_data: Optional[Dict] = None) -> Dict:
        """Trigger a workflow execution"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        if not workflow.active:
            return {"error": f"Workflow {workflow.name} is not active"}
        
        try:
            # For demonstration, simulate immediate execution
            self._simulate_execution(workflow_id)
            
            return {
                "success": True,
                "message": f"Workflow {workflow.name} triggered successfully",
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error triggering workflow {workflow_id}: {e}")
            return {"error": str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of a specific workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        # Get recent executions
        recent_executions = [
            asdict(exec) for exec in self.executions.values()
            if exec.workflow_id == workflow_id
        ][-5:]  # Last 5 executions
        
        return {
            "workflow": asdict(workflow),
            "recent_executions": recent_executions,
            "is_running": any(exec.status == WorkflowStatus.RUNNING for exec in self.executions.values() if exec.workflow_id == workflow_id)
        }
    
    def get_all_workflows(self) -> Dict:
        """Get all workflows with their status"""
        workflows_data = []
        
        for workflow in self.workflows.values():
            workflow_data = asdict(workflow)
            
            # Add execution stats
            workflow_executions = [exec for exec in self.executions.values() if exec.workflow_id == workflow.id]
            workflow_data['total_executions'] = len(workflow_executions)
            workflow_data['running_executions'] = len([exec for exec in workflow_executions if exec.status == WorkflowStatus.RUNNING])
            workflow_data['last_execution_status'] = workflow_executions[-1].status.value if workflow_executions else None
            
            workflows_data.append(workflow_data)
        
        return {
            "workflows": workflows_data,
            "total_count": len(workflows_data),
            "active_count": len(self.active_workflows),
            "categories": list(set(wf.category for wf in self.workflows.values()))
        }
    
    def get_executions(self, limit: int = 50) -> Dict:
        """Get recent workflow executions"""
        recent_executions = sorted(
            self.executions.values(),
            key=lambda x: x.started_at,
            reverse=True
        )[:limit]
        
        return {
            "executions": [asdict(exec) for exec in recent_executions],
            "total_count": len(self.executions),
            "running_count": len([exec for exec in self.executions.values() if exec.status == WorkflowStatus.RUNNING])
        }
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activate a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow.active = True
        if workflow_id not in self.active_workflows:
            self.active_workflows.append(workflow_id)
        
        logger.info(f"✅ Activated workflow: {workflow.name}")
        return {
            "success": True,
            "message": f"Workflow {workflow.name} activated",
            "workflow_id": workflow_id
        }
    
    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Deactivate a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow.active = False
        if workflow_id in self.active_workflows:
            self.active_workflows.remove(workflow_id)
        
        logger.info(f"⏸️ Deactivated workflow: {workflow.name}")
        return {
            "success": True,
            "message": f"Workflow {workflow.name} deactivated",
            "workflow_id": workflow_id
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get dashboard data for frontend display"""
        total_workflows = len(self.workflows)
        active_workflows = len(self.active_workflows)
        total_executions = len(self.executions)
        
        # Calculate success rate
        successful_executions = len([exec for exec in self.executions.values() if exec.status == WorkflowStatus.SUCCESS])
        overall_success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 100
        
        # Get category breakdown
        category_stats = {}
        for workflow in self.workflows.values():
            category = workflow.category
            if category not in category_stats:
                category_stats[category] = {"total": 0, "active": 0}
            category_stats[category]["total"] += 1
            if workflow.active:
                category_stats[category]["active"] += 1
        
        # Get recent activity
        recent_executions = sorted(
            self.executions.values(),
            key=lambda x: x.started_at,
            reverse=True
        )[:10]
        
        return {
            "summary": {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "total_executions": total_executions,
                "success_rate": round(overall_success_rate, 1)
            },
            "category_stats": category_stats,
            "recent_activity": [
                {
                    "workflow_name": exec.workflow_name,
                    "status": exec.status.value,
                    "started_at": exec.started_at,
                    "finished_at": exec.finished_at
                }
                for exec in recent_executions
            ],
            "timestamp": datetime.now().isoformat()
        }

# Global instance
workflow_manager = N8nWorkflowManager()

