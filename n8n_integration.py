#!/usr/bin/env python3
"""
n8n Integration Module for XMRT-Ecosystem
=========================================

This module integrates n8n workflow capabilities into the XMRT-Ecosystem,
providing autonomous workflow execution and management for Eliza.

Author: Manus AI
Date: 2025-01-09
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime
import threading
import time

# Import the workflow manager
sys.path.append('/home/ubuntu')
from n8n_workflow_manager import workflow_manager, WorkflowStatus

logger = logging.getLogger(__name__)

def create_n8n_blueprint():
    """Create Flask blueprint for n8n integration"""
    
    n8n_bp = Blueprint('n8n_integration', __name__, url_prefix='/api/n8n')
    
    @n8n_bp.route('/workflows', methods=['GET'])
    def get_workflows():
        """Get all workflows"""
        try:
            return jsonify(workflow_manager.get_all_workflows())
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/workflows/<workflow_id>', methods=['GET'])
    def get_workflow(workflow_id):
        """Get specific workflow status"""
        try:
            return jsonify(workflow_manager.get_workflow_status(workflow_id))
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/workflows/<workflow_id>/trigger', methods=['POST'])
    def trigger_workflow(workflow_id):
        """Trigger a workflow execution"""
        try:
            data = request.get_json() or {}
            result = workflow_manager.trigger_workflow(workflow_id, data)
            
            # Add to activity feed if successful
            if result.get('success'):
                from main import add_activity_item
                add_activity_item('operation', f"n8n workflow triggered: {result.get('message', 'Unknown workflow')}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error triggering workflow {workflow_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/workflows/<workflow_id>/activate', methods=['POST'])
    def activate_workflow(workflow_id):
        """Activate a workflow"""
        try:
            result = workflow_manager.activate_workflow(workflow_id)
            
            if result.get('success'):
                from main import add_activity_item
                add_activity_item('operation', f"n8n workflow activated: {result.get('message', 'Unknown workflow')}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/workflows/<workflow_id>/deactivate', methods=['POST'])
    def deactivate_workflow(workflow_id):
        """Deactivate a workflow"""
        try:
            result = workflow_manager.deactivate_workflow(workflow_id)
            
            if result.get('success'):
                from main import add_activity_item
                add_activity_item('operation', f"n8n workflow deactivated: {result.get('message', 'Unknown workflow')}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error deactivating workflow {workflow_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/executions', methods=['GET'])
    def get_executions():
        """Get workflow executions"""
        try:
            limit = int(request.args.get('limit', 50))
            return jsonify(workflow_manager.get_executions(limit))
        except Exception as e:
            logger.error(f"Error getting executions: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/dashboard', methods=['GET'])
    def get_dashboard():
        """Get dashboard data for frontend"""
        try:
            return jsonify(workflow_manager.get_dashboard_data())
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/status', methods=['GET'])
    def get_status():
        """Get n8n integration status"""
        try:
            return jsonify({
                "status": "active",
                "monitoring_active": workflow_manager.monitoring_active,
                "total_workflows": len(workflow_manager.workflows),
                "active_workflows": len(workflow_manager.active_workflows),
                "total_executions": len(workflow_manager.executions),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({"error": str(e)}), 500
    
    @n8n_bp.route('/autonomous/trigger', methods=['POST'])
    def autonomous_trigger():
        """Trigger workflows autonomously based on context"""
        try:
            data = request.get_json() or {}
            context = data.get('context', 'general')
            
            # Determine which workflows to trigger based on context
            triggered_workflows = []
            
            if context == 'memory_update':
                # Trigger memory-related workflows
                memory_workflows = [wf_id for wf_id, wf in workflow_manager.workflows.items() 
                                  if wf.category == 'long_term_memory' and wf.active]
                for wf_id in memory_workflows[:2]:  # Trigger up to 2 workflows
                    result = workflow_manager.trigger_workflow(wf_id)
                    if result.get('success'):
                        triggered_workflows.append(wf_id)
            
            elif context == 'system_check':
                # Trigger system administration workflows
                sysadmin_workflows = [wf_id for wf_id, wf in workflow_manager.workflows.items() 
                                    if wf.category == 'systems_administration' and wf.active]
                for wf_id in sysadmin_workflows[:1]:  # Trigger 1 workflow
                    result = workflow_manager.trigger_workflow(wf_id)
                    if result.get('success'):
                        triggered_workflows.append(wf_id)
            
            elif context == 'business_update':
                # Trigger business management workflows
                business_workflows = [wf_id for wf_id, wf in workflow_manager.workflows.items() 
                                    if wf.category == 'c_suite_business_management' and wf.active]
                for wf_id in business_workflows[:2]:  # Trigger up to 2 workflows
                    result = workflow_manager.trigger_workflow(wf_id)
                    if result.get('success'):
                        triggered_workflows.append(wf_id)
            
            else:
                # General context - trigger a mix of workflows
                active_workflows = [wf_id for wf_id, wf in workflow_manager.workflows.items() if wf.active]
                import random
                selected_workflows = random.sample(active_workflows, min(3, len(active_workflows)))
                for wf_id in selected_workflows:
                    result = workflow_manager.trigger_workflow(wf_id)
                    if result.get('success'):
                        triggered_workflows.append(wf_id)
            
            # Add to activity feed
            if triggered_workflows:
                from main import add_activity_item
                add_activity_item('operation', f"Autonomous n8n execution: {len(triggered_workflows)} workflows triggered for {context}")
            
            return jsonify({
                "success": True,
                "message": f"Autonomous trigger completed for context: {context}",
                "triggered_workflows": triggered_workflows,
                "count": len(triggered_workflows),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in autonomous trigger: {e}")
            return jsonify({"error": str(e)}), 500
    
    return n8n_bp

def initialize_n8n_integration():
    """Initialize n8n integration"""
    try:
        # Start workflow monitoring
        workflow_manager.start_monitoring()
        
        # Add initial activity
        from main import add_activity_item
        add_activity_item('operation', 'n8n workflow integration initialized - Autonomous capabilities active')
        
        logger.info("🤖 n8n integration initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing n8n integration: {e}")
        return False

def autonomous_workflow_scheduler():
    """Background scheduler for autonomous workflow execution"""
    import random
    
    while True:
        try:
            # Randomly trigger autonomous workflows
            if random.random() > 0.7:  # 30% chance every cycle
                contexts = ['memory_update', 'system_check', 'business_update', 'general']
                context = random.choice(contexts)
                
                # Simulate autonomous trigger
                active_workflows = [wf_id for wf_id, wf in workflow_manager.workflows.items() if wf.active]
                if active_workflows:
                    selected_workflow = random.choice(active_workflows)
                    result = workflow_manager.trigger_workflow(selected_workflow)
                    
                    if result.get('success'):
                        from main import add_activity_item
                        workflow_name = workflow_manager.workflows[selected_workflow].name
                        add_activity_item('operation', f"Autonomous execution: {workflow_name} completed successfully")
            
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in autonomous scheduler: {e}")
            time.sleep(120)  # Wait longer on error

def start_autonomous_scheduler():
    """Start the autonomous workflow scheduler"""
    scheduler_thread = threading.Thread(target=autonomous_workflow_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("🔄 Autonomous workflow scheduler started")

