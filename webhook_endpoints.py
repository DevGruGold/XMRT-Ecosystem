#!/usr/bin/env python3
"""
Webhook Endpoints for XMRT Ecosystem Inter-System Communication
===============================================================

This module provides webhook endpoints that can be added to each of the three
XMRT DAO pillars to enable real-time communication while preserving their
separate architectures.

Author: Manus AI
Date: 2025-08-13
"""

from flask import Flask, request, jsonify, Blueprint
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

def create_ecosystem_webhook_blueprint():
    """
    Create a Flask blueprint with webhook endpoints for ecosystem communication
    This can be added to any of the three systems without modifying their core architecture
    """
    
    webhook_bp = Blueprint('ecosystem_webhook', __name__, url_prefix='/api')
    
    # Store for received activities (in-memory for simplicity)
    received_activities = []
    ecosystem_state = {}
    
    @webhook_bp.route('/webhook/receive', methods=['POST'])
    def receive_webhook():
        """Receive webhook from other systems in the ecosystem"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['source_system', 'event_type', 'data', 'timestamp', 'event_id']
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
            
            # Store the activity
            activity = {
                "source_system": data['source_system'],
                "event_type": data['event_type'],
                "data": data['data'],
                "timestamp": data['timestamp'],
                "event_id": data['event_id'],
                "received_at": datetime.now().isoformat()
            }
            
            received_activities.append(activity)
            
            # Keep only last 100 activities
            if len(received_activities) > 100:
                received_activities.pop(0)
            
            logger.info(f"📨 Received {data['event_type']} from {data['source_system']}")
            
            return jsonify({
                "success": True,
                "message": "Activity received successfully",
                "event_id": data['event_id']
            })
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({"error": str(e)}), 500
    
    @webhook_bp.route('/ecosystem/sync', methods=['POST'])
    def sync_ecosystem_state():
        """Receive ecosystem state synchronization"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Update ecosystem state
            ecosystem_state.update(data)
            ecosystem_state['last_sync'] = datetime.now().isoformat()
            
            logger.info("🔄 Ecosystem state synchronized")
            
            return jsonify({
                "success": True,
                "message": "Ecosystem state synchronized",
                "timestamp": ecosystem_state['last_sync']
            })
            
        except Exception as e:
            logger.error(f"Error syncing ecosystem state: {e}")
            return jsonify({"error": str(e)}), 500
    
    @webhook_bp.route('/ecosystem/activities', methods=['GET'])
    def get_ecosystem_activities():
        """Get received activities from other systems"""
        try:
            # Filter activities by type if requested
            event_type = request.args.get('event_type')
            source_system = request.args.get('source_system')
            limit = int(request.args.get('limit', 50))
            
            filtered_activities = received_activities
            
            if event_type:
                filtered_activities = [a for a in filtered_activities if a['event_type'] == event_type]
            
            if source_system:
                filtered_activities = [a for a in filtered_activities if a['source_system'] == source_system]
            
            # Apply limit
            filtered_activities = filtered_activities[-limit:]
            
            return jsonify({
                "success": True,
                "activities": filtered_activities,
                "total_count": len(filtered_activities),
                "ecosystem_state": ecosystem_state
            })
            
        except Exception as e:
            logger.error(f"Error getting ecosystem activities: {e}")
            return jsonify({"error": str(e)}), 500
    
    @webhook_bp.route('/ecosystem/status', methods=['GET'])
    def get_ecosystem_status():
        """Get current ecosystem coordination status"""
        try:
            status = {
                "webhook_active": True,
                "received_activities_count": len(received_activities),
                "last_activity": received_activities[-1] if received_activities else None,
                "ecosystem_state": ecosystem_state,
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify({
                "success": True,
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Error getting ecosystem status: {e}")
            return jsonify({"error": str(e)}), 500
    
    @webhook_bp.route('/activity/feed', methods=['GET'])
    def get_activity_feed():
        """Get activity feed for frontend display"""
        try:
            # Get recent activities formatted for frontend
            limit = int(request.args.get('limit', 20))
            recent_activities = received_activities[-limit:]
            
            # Format activities for display
            formatted_activities = []
            for activity in recent_activities:
                formatted_activity = {
                    "id": activity['event_id'],
                    "title": _format_activity_title(activity),
                    "description": _format_activity_description(activity),
                    "source": activity['source_system'],
                    "timestamp": activity['timestamp'],
                    "type": activity['event_type'],
                    "data": activity['data']
                }
                formatted_activities.append(formatted_activity)
            
            return jsonify({
                "success": True,
                "activities": formatted_activities,
                "total_count": len(formatted_activities)
            })
            
        except Exception as e:
            logger.error(f"Error getting activity feed: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _format_activity_title(activity):
        """Format activity title for display"""
        event_type = activity['event_type']
        source = activity['source_system']
        
        titles = {
            'growth_update': f"📈 Growth Metrics Updated",
            'system_status': f"🔧 System Status from {source.title()}",
            'agent_discussion': f"💬 Agent Discussion in {source.title()}",
            'mining_update': f"⛏️ Mining Stats Updated",
            'meshnet_update': f"📡 MESHNET Status Updated"
        }
        
        return titles.get(event_type, f"🔔 {event_type.replace('_', ' ').title()}")
    
    def _format_activity_description(activity):
        """Format activity description for display"""
        event_type = activity['event_type']
        data = activity['data']
        
        if event_type == 'growth_update':
            health = data.get('overall_health', 'Unknown')
            return f"Overall health: {health}, Motivation level updated"
        
        elif event_type == 'agent_discussion':
            agent_name = data.get('agent_name', 'Agent')
            message = data.get('message', '')[:100] + '...' if len(data.get('message', '')) > 100 else data.get('message', '')
            return f"{agent_name}: {message}"
        
        elif event_type == 'mining_update':
            hashrate = data.get('total_hashrate', 'Unknown')
            miners = data.get('active_miners', 'Unknown')
            return f"Hashrate: {hashrate}, Active miners: {miners}"
        
        elif event_type == 'meshnet_update':
            nodes = data.get('active_nodes', 'Unknown')
            coverage = data.get('network_coverage', 'Unknown')
            return f"Active nodes: {nodes}, Coverage: {coverage}"
        
        else:
            return f"Activity from {activity['source_system']}"
    
    return webhook_bp

# Standalone Flask app for testing
def create_test_app():
    """Create a test Flask app with webhook endpoints"""
    app = Flask(__name__)
    app.register_blueprint(create_ecosystem_webhook_blueprint())
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "XMRT Ecosystem Webhook Service",
            "endpoints": [
                "/api/webhook/receive",
                "/api/ecosystem/sync", 
                "/api/ecosystem/activities",
                "/api/ecosystem/status",
                "/api/activity/feed"
            ]
        })
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    app.run(host='0.0.0.0', port=5001)

