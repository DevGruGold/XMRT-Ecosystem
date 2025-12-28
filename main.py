#!/usr/bin/env python3
"""
XMRT Ecosystem - Main Application Entry Point
Integrates the activity monitor API with enhanced real-time features
"""

import os
import sys
import logging
from flask import Flask, render_template_string, send_from_directory
from flask_cors import CORS
import json
import time
import threading
import random
from datetime import datetime, timedelta
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global state for activity monitoring
activity_state = {
    'agents': {
        'dao_governor': {'status': 'active', 'last_action': 'Analyzing proposal #247', 'last_update': time.time()},
        'defi_specialist': {'status': 'active', 'last_action': 'Optimizing yield strategy', 'last_update': time.time()},
        'security_guardian': {'status': 'active', 'last_action': 'Scanning for threats', 'last_update': time.time()},
        'community_manager': {'status': 'active', 'last_action': 'Analyzing sentiment', 'last_update': time.time()}
    },
    'communications': [],
    'operations': [],
    'metrics': {
        'active_agents': 4,
        'decisions_made': 156,
        'community_count': 1247,
        'uptime': 99.8
    },
    'system_active': True,
    'autonomous_communication_active': True,
    'total_messages': 0
}

# Enhanced agent actions for more realistic simulation
agent_actions = [
    "DAO Governor: Analyzing new governance proposal for treasury allocation",
    "DeFi Specialist: Optimizing yield farming strategy across multiple protocols", 
    "Security Guardian: Performing comprehensive security audit on smart contracts",
    "Community Manager: Processing community feedback and sentiment analysis",
    "DAO Governor → DeFi Specialist: Requesting detailed treasury analysis report",
    "Security Guardian: Threat assessment completed - All systems secure",
    "Community Manager: Sentiment analysis updated - Community engagement up 15%",
    "DeFi Specialist: Liquidity rebalancing executed - APY improved to 12.3%",
    "DAO Governor: Multi-signature transaction initiated for protocol upgrade",
    "Security Guardian: Vulnerability scan completed - Zero critical issues found",
    "Community Manager: Event coordination in progress - DAO meetup scheduled",
    "DeFi Specialist: Cross-chain bridge operation successful - 50K XMRT transferred",
    "DAO Governor: Proposal #248 passed with 89% approval rate",
    "Security Guardian: Emergency circuit breaker tested - Response time 0.3s",
    "Community Manager: New member onboarding - 25 new participants this week",
    "DeFi Specialist: Automated arbitrage opportunity detected - Profit: $2,340"
]

system_operations = [
    "Smart contract deployment successful - Gas optimized by 23%",
    "Cross-chain bridge operation completed - Transaction hash: 0x7f3a...", 
    "Treasury rebalancing executed - Portfolio diversification improved",
    "Automated backup completed - All data secured across 3 locations",
    "Performance optimization applied - Response time improved by 40%",
    "Security scan completed - All systems operational and secure",
    "Code improvement deployed - Bug fixes and feature enhancements live",
    "Network synchronization completed - All nodes in consensus",
    "Emergency circuit breaker tested - Failsafe mechanisms verified",
    "Multi-chain governance sync completed - Cross-chain voting enabled",
    "Zero-knowledge proof verification successful - Privacy maintained",
    "Automated incident response triggered - Issue resolved in 2.1 minutes",
    "Database optimization completed - Query performance improved 60%",
    "Load balancer configuration updated - Traffic distribution optimized",
    "API rate limiting adjusted - DDoS protection enhanced",
    "Monitoring alerts configured - Real-time threat detection active"
]

def add_activity_item(activity_type, message):
    """Add a new activity item to the appropriate feed"""
    timestamp = datetime.now().isoformat()
    item = {
        'message': message,
        'timestamp': timestamp,
        'id': int(time.time() * 1000)  # Unique ID
    }
    
    if activity_type == 'communication':
        activity_state['communications'].insert(0, item)
        # Keep only last 15 items
        activity_state['communications'] = activity_state['communications'][:15]
        activity_state['total_messages'] += 1
    elif activity_type == 'operation':
        activity_state['operations'].insert(0, item)
        # Keep only last 15 items
        activity_state['operations'] = activity_state['operations'][:15]
    
    logger.info(f"Added {activity_type}: {message}")

def simulate_activity():
    """Background thread to simulate enhanced agent activity"""
    logger.info("🤖 Starting autonomous operations with inter-agent communication")
    
    while True:
        if activity_state['system_active'] and activity_state['autonomous_communication_active']:
            # More frequent agent communications (70% chance)
            if random.random() > 0.3:
                action = random.choice(agent_actions)
                add_activity_item('communication', action)
            
            # System operations (40% chance)
            if random.random() > 0.6:
                operation = random.choice(system_operations)
                add_activity_item('operation', operation)
            
            # Update agent statuses more frequently
            if random.random() > 0.7:
                update_agent_statuses()
            
            # Update metrics occasionally
            if random.random() > 0.85:
                update_metrics()
        
        # Shorter sleep for more active simulation
        time.sleep(random.randint(8, 20))  # Random interval between 8-20 seconds

def update_agent_statuses():
    """Update agent statuses with more detailed activities"""
    activities = {
        'dao_governor': [
            'Analyzing governance proposal #249',
            'Coordinating multi-sig transaction',
            'Reviewing treasury allocation',
            'Processing community votes',
            'Evaluating protocol upgrade'
        ],
        'defi_specialist': [
            'Optimizing yield strategies',
            'Monitoring liquidity pools',
            'Executing arbitrage trades',
            'Rebalancing portfolio',
            'Analyzing market trends'
        ],
        'security_guardian': [
            'Scanning for vulnerabilities',
            'Monitoring threat landscape',
            'Auditing smart contracts',
            'Testing security protocols',
            'Analyzing transaction patterns'
        ],
        'community_manager': [
            'Analyzing community sentiment',
            'Coordinating events',
            'Processing member feedback',
            'Managing social channels',
            'Tracking engagement metrics'
        ]
    }
    
    for agent_id in activity_state['agents']:
        if random.random() > 0.6:  # 40% chance to update each agent
            agent = activity_state['agents'][agent_id]
            if agent_id in activities:
                agent['last_action'] = random.choice(activities[agent_id])
                agent['last_update'] = time.time()

def update_metrics():
    """Update system metrics with more realistic changes"""
    metrics = activity_state['metrics']
    
    # Gradually increase community count
    if random.random() > 0.7:
        metrics['community_count'] += random.randint(1, 8)
    
    # Increment decisions made
    if random.random() > 0.8:
        metrics['decisions_made'] += random.randint(1, 3)
    
    # Slight uptime variations
    if random.random() > 0.95:
        metrics['uptime'] = max(98.0, min(99.9, metrics['uptime'] + random.uniform(-0.1, 0.1)))

def check_external_service():
    """Check if the external XMRT service is active"""
    try:
        response = requests.get('https://xmrtnet-eliza.onrender.com/', timeout=5)
        return response.status_code == 200
    except:
        return False

# Serve the main HTML file
@app.route('/')
def index():
    """Serve the main dashboard"""
    try:
        with open('index_fixed.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # Fallback to basic HTML if file not found
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>XMRT DAO Hub - Loading...</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .loading { color: #666; }
            </style>
        </head>
        <body>
            <h1>XMRT DAO Hub</h1>
            <p class="loading">Loading dashboard...</p>
            <script>
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            </script>
        </body>
        </html>
        """

@app.route('/api/status')
def get_status():
    """Get overall system status"""
    external_active = check_external_service()
    
    return {
        'active': activity_state['system_active'],
        'external_service_active': external_active,
        'agents': activity_state['agents'],
        'metrics': activity_state['metrics'],
        'autonomous_communication_active': activity_state['autonomous_communication_active'],
        'total_messages': activity_state['total_messages'],
        'active_discussions': len([c for c in activity_state['communications'] if 'discussion' in c['message'].lower()]),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/activity/feed')
def get_activity_feed():
    """Get the current activity feed"""
    return {
        'communications': activity_state['communications'],
        'operations': activity_state['operations'],
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Trigger a new agent discussion"""
    from flask import request
    
    data = request.get_json() or {}
    topic = data.get('topic', 'general_coordination')
    
    logger.info(f"🤖 Initiating autonomous discussion on: {topic}")
    
    # Add discussion activities
    add_activity_item('communication', f'DAO Governor: Initiating multi-agent discussion on {topic.replace("_", " ")}')
    add_activity_item('communication', 'DeFi Specialist: Joining discussion with current yield analysis')
    add_activity_item('communication', 'Security Guardian: Providing security assessment for proposed changes')
    add_activity_item('communication', 'Community Manager: Contributing sentiment analysis data')
    
    # Try to trigger actual external service
    try:
        requests.post('https://xmrtnet-eliza.onrender.com/api/trigger-discussion', 
                     json={'topic': topic}, timeout=5)
        add_activity_item('operation', 'External AI service discussion triggered successfully')
    except:
        add_activity_item('operation', 'External AI service unavailable - using autonomous simulation')
    
    activity_state['system_active'] = True
    activity_state['autonomous_communication_active'] = True
    
    return {
        'success': True,
        'message': f'Discussion on {topic} initiated',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/start-analysis', methods=['POST'])
def start_analysis():
    """Start a comprehensive analysis task"""
    from flask import request
    
    data = request.get_json() or {}
    analysis_type = data.get('type', 'ecosystem_health')
    
    logger.info(f"🤖 Starting analysis task: {analysis_type}")
    
    # Add analysis activities
    add_activity_item('operation', f'Analysis task initiated: {analysis_type.replace("_", " ")} assessment')
    add_activity_item('operation', 'Data collection started across all monitored protocols')
    add_activity_item('operation', 'Multi-agent coordination for comprehensive analysis')
    
    # Update agent statuses to show analysis work
    activity_state['agents']['dao_governor']['last_action'] = 'Coordinating comprehensive analysis task'
    activity_state['agents']['defi_specialist']['last_action'] = 'Analyzing DeFi protocols and yield opportunities'
    activity_state['agents']['security_guardian']['last_action'] = 'Security assessment and threat analysis in progress'
    activity_state['agents']['community_manager']['last_action'] = 'Community impact and sentiment analysis'
    
    # Try to trigger actual external service
    try:
        requests.post('https://xmrtnet-eliza.onrender.com/api/start-analysis',
                     json={'type': analysis_type}, timeout=5)
        add_activity_item('operation', 'External AI service analysis started successfully')
    except:
        add_activity_item('operation', 'External AI service unavailable - using autonomous analysis')
    
    activity_state['system_active'] = True
    
    return {
        'success': True,
        'message': f'Analysis of {analysis_type} started',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/agents/<agent_id>/status')
def get_agent_status(agent_id):
    """Get status of a specific agent"""
    if agent_id in activity_state['agents']:
        return activity_state['agents'][agent_id]
    else:
        return {'error': 'Agent not found'}, 404

@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics"""
    return activity_state['metrics']

@app.route('/api/kickstart', methods=['POST'])
def kickstart_system():
    """Kickstart system activity if idle"""
    logger.info("✅ Autonomous communication system started")
    
    activity_state['system_active'] = True
    activity_state['autonomous_communication_active'] = True
    
    # Add kickstart activities
    add_activity_item('operation', 'System activity kickstarted - All agents reactivated')
    add_activity_item('communication', 'DAO Governor: System reactivation complete - Resuming governance operations')
    add_activity_item('communication', 'All agents: Autonomous operations resumed - Inter-agent communication active')
    
    # Reset all agent statuses
    for agent_id in activity_state['agents']:
        activity_state['agents'][agent_id]['status'] = 'active'
        activity_state['agents'][agent_id]['last_update'] = time.time()
    
    return {
        'success': True,
        'message': 'Autonomous communication system activated',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time,
        'active_agents': len([a for a in activity_state['agents'].values() if a['status'] == 'active']),
        'total_communications': len(activity_state['communications']),
        'total_operations': len(activity_state['operations'])
    }

if __name__ == '__main__':
    start_time = time.time()
    
    # Initialize n8n integration
    try:
        from n8n_integration import create_n8n_blueprint, initialize_n8n_integration, start_autonomous_scheduler
        
        # Register n8n blueprint
        n8n_bp = create_n8n_blueprint()
        app.register_blueprint(n8n_bp)
        
        # Initialize n8n integration
        initialize_n8n_integration()
        
        # Start autonomous scheduler
        start_autonomous_scheduler()
        
        logger.info("🤖 n8n integration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load n8n integration: {e}")
    
    # Initialize with enhanced sample activities
    logger.info("Loaded 4 AI characters with autonomous communication")
    add_activity_item('communication', 'DAO Governor: Enhanced system initialization complete')
    add_activity_item('operation', 'All systems online - Real-time monitoring active')
    add_activity_item('communication', 'Security Guardian: Initial security scan completed - All systems secure')
    add_activity_item('communication', 'DeFi Specialist: Yield optimization protocols loaded and active')
    add_activity_item('communication', 'Community Manager: Community engagement tracking initialized')
    add_activity_item('operation', 'n8n workflow system integrated - Autonomous capabilities enhanced')
    
    # Start background activity simulation
    activity_thread = threading.Thread(target=simulate_activity, daemon=True)
    activity_thread.start()
    
    logger.info("Enhanced chat system initialized successfully")
    
    print("XMRT DAO Hub - Enhanced Activity Monitor starting...")
    print("Available endpoints:")
    print("  GET  / - Main dashboard")
    print("  GET  /api/status - System status")
    print("  GET  /api/activity/feed - Activity feed")
    print("  POST /api/trigger-discussion - Trigger discussion")
    print("  POST /api/start-analysis - Start analysis")
    print("  POST /api/kickstart - Kickstart system")
    print("  GET  /api/health - Health check")
    print("  GET  /api/n8n/workflows - n8n workflows")
    print("  GET  /api/n8n/dashboard - n8n dashboard")
    print("  POST /api/n8n/autonomous/trigger - Autonomous workflow trigger")
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False)

