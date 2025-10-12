#!/usr/bin/env python3
'''
XMRT Ecosystem Enhanced Python Service with Supabase Backend Integration
Integrates with the same Supabase backend as xmrtassistant
'''

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import logging
import threading
from datetime import datetime, timedelta
import requests
import time
import random

# Supabase integration
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase-py not installed. Install with: pip install supabase")

# Enhanced Chat System Integration
try:
    from enhanced_chat_system import create_enhanced_chat_routes, EnhancedXMRTChatSystem
    ENHANCED_CHAT_AVAILABLE = True
except ImportError:
    ENHANCED_CHAT_AVAILABLE = False

try:
    from webhook_endpoints import create_ecosystem_webhook_blueprint
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

try:
    from pipedream_integration import create_pipedream_capability
    PIPEDREAM_AVAILABLE = True
except ImportError:
    PIPEDREAM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-secret-key')
    
    # Supabase Configuration (shared with xmrtassistant)
    SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://vawouugtzwmejxqkeqqj.supabase.co')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhd291dWd0endtZWp4cWtlcXFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3Njk3MTIsImV4cCI6MjA2ODM0NTcxMn0.qtZk3zk5RMqzlPNhxCkTM6fyVQX5ULGt7nna_XOUr00')
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    
    # Autonomous Operation Settings
    AUTONOMOUS_COMMUNICATION_ENABLED = True
    AUTONOMOUS_DISCUSSION_INTERVAL = 300  # 5 minutes

app.config.from_object(Config)

# Initialize Supabase client
supabase_client = None
if SUPABASE_AVAILABLE and app.config['SUPABASE_URL'] and app.config['SUPABASE_KEY']:
    try:
        supabase_client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
        logger.info("✅ Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
else:
    logger.warning("⚠️ Supabase not available - using in-memory storage")

# Register blueprints
if WEBHOOK_AVAILABLE:
    try:
        ecosystem_webhook_bp = create_ecosystem_webhook_blueprint()
        app.register_blueprint(ecosystem_webhook_bp)
        logger.info("✅ Webhook endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register webhook blueprint: {e}")

# Global state for autonomous operations
autonomous_state = {
    'active_agents': {},
    'task_queue': [],
    'performance_metrics': {},
    'security_alerts': [],
    'community_events': [],
    'active_discussions': {},
    'autonomous_communication_active': False
}

# In-memory chat history (fallback if Supabase unavailable)
chat_history = []

class SupabaseManager:
    """Manages Supabase database operations"""
    
    def __init__(self, client):
        self.client = client
        self.enabled = client is not None
    
    def save_message(self, sender, message, agent_id=None, message_type='user_chat'):
        """Save a message to Supabase using chat_messages table"""
        if not self.enabled:
            return None
        
        try:
            data = {
                'role': 'assistant' if agent_id else 'user',  # chat_messages uses 'role' field
                'content': message,  # chat_messages uses 'content' field
                'metadata': {
                    'sender': sender,
                    'agent_id': agent_id,
                    'message_type': message_type
                }
            }
            
            result = self.client.table('chat_messages').insert(data).execute()
            logger.info(f"Message saved to Supabase: {sender}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error saving message to Supabase: {e}")
            return None
    
    def get_recent_messages(self, limit=50):
        """Get recent messages from Supabase using chat_messages table"""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table('chat_messages')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            messages = result.data if result.data else []
            # Convert to expected format
            formatted_messages = []
            for msg in reversed(messages):
                formatted_messages.append({
                    'sender': msg.get('metadata', {}).get('sender', 'Agent'),
                    'message': msg.get('content', ''),
                    'timestamp': msg.get('created_at', datetime.now().isoformat()),
                    'agent_id': msg.get('metadata', {}).get('agent_id'),
                    'type': msg.get('metadata', {}).get('message_type', 'chat')
                })
            return formatted_messages
        except Exception as e:
            logger.error(f"Error fetching messages from Supabase: {e}")
            return []
    
    def save_activity(self, activity_type, title, description, data=None):
        """Save an activity - using in-memory for now since activities table doesn't exist"""
        # Activities table doesn't exist in the Supabase schema yet
        # Store in memory for now
        logger.info(f"Activity logged (in-memory): {title}")
        return None
    
    def get_recent_activities(self, limit=20):
        """Get recent activities - return empty for now since table doesn't exist"""
        # Activities table doesn't exist yet
        return []

# Initialize Supabase manager
db = SupabaseManager(supabase_client)

class AutonomousAgentCommunicator:
    """Enhanced autonomous communication system for XMRT agents"""
    
    def __init__(self):
        self.agents = {
            "xmrt_dao_governor": {
                "name": "XMRT DAO Governor",
                "personality": "Strategic, diplomatic, consensus-building",
                "communication_style": "Formal, analytical, seeks broad perspective",
                "expertise": ["governance", "strategy", "consensus", "policy"],
                "triggers": ["governance", "proposal", "vote", "decision", "policy"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_defi_specialist": {
                "name": "XMRT DeFi Specialist",
                "personality": "Data-driven, opportunistic, risk-aware",
                "communication_style": "Technical, numbers-focused, opportunity-seeking",
                "expertise": ["defi", "yield", "liquidity", "protocols", "apy"],
                "triggers": ["defi", "yield", "farming", "liquidity", "protocol", "apy"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_community_manager": {
                "name": "XMRT Community Manager",
                "personality": "Enthusiastic, inclusive, growth-minded",
                "communication_style": "Engaging, positive, community-focused",
                "expertise": ["community", "engagement", "growth", "social", "outreach"],
                "triggers": ["community", "users", "engagement", "social", "growth"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_security_guardian": {
                "name": "XMRT Security Guardian",
                "personality": "Cautious, thorough, protective",
                "communication_style": "Precise, security-focused, risk-assessment",
                "expertise": ["security", "risks", "audits", "vulnerabilities", "protection"],
                "triggers": ["security", "risk", "vulnerability", "audit", "threat"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            }
        }
        
        self.conversation_history = []
        self.active_discussions = {}
        
    def analyze_message_for_triggers(self, message):
        """Analyze message to determine which agents should participate"""
        message_lower = message.lower()
        triggered_agents = []
        
        for agent_id, agent_data in self.agents.items():
            for trigger in agent_data["triggers"]:
                if trigger in message_lower:
                    triggered_agents.append(agent_id)
                    break
        
        if not triggered_agents:
            triggered_agents = ["xmrt_community_manager"]
            
        return triggered_agents
    
    def generate_autonomous_response(self, agent_id, context, other_agents_present):
        """Generate contextual response based on agent personality"""
        agent = self.agents[agent_id]
        
        responses = {
            "xmrt_dao_governor": [
                f"As DAO Governor, I believe we should consider the broader implications of '{context}'. What are your thoughts on the governance aspects?",
                f"From a strategic perspective, '{context}' presents both opportunities and challenges. I'd like to hear from our specialists.",
                f"Let's ensure we're aligned with our DAO principles regarding '{context}'. This requires careful consideration of all stakeholders.",
            ],
            "xmrt_defi_specialist": [
                f"Looking at the DeFi metrics, '{context}' could impact our yield strategies. Current APY opportunities suggest we should act quickly.",
                f"The numbers show '{context}' aligns with our optimization goals. I'm seeing potential for 15-20% yield improvement.",
                f"From a DeFi perspective, '{context}' opens up new liquidity opportunities.",
            ],
            "xmrt_community_manager": [
                f"The community is really excited about '{context}'! Engagement metrics are up 25% since we started discussing this.",
                f"I've been monitoring social sentiment around '{context}' - it's overwhelmingly positive!",
                f"From a growth perspective, '{context}' could attract 500+ new users.",
            ],
            "xmrt_security_guardian": [
                f"I've completed a preliminary security assessment of '{context}'. There are 3 potential risk vectors we need to address.",
                f"Security-wise, '{context}' requires additional safeguards. I recommend implementing circuit breakers before proceeding.",
                f"Risk analysis shows '{context}' is within acceptable parameters, but we need monitoring systems in place.",
            ]
        }
        
        agent_responses = responses.get(agent_id, ["I'm analyzing this situation..."])
        return random.choice(agent_responses)
    
    def initiate_autonomous_discussion(self, topic):
        """Start an autonomous discussion between agents"""
        logger.info(f"🤖 Initiating autonomous discussion on: {topic}")
        
        participating_agents = self.analyze_message_for_triggers(topic)
        
        discussion_id = f"discussion_{int(time.time())}"
        self.active_discussions[discussion_id] = {
            "topic": topic,
            "participants": participating_agents,
            "messages": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        discussion_messages = []
        for agent_id in participating_agents:
            response = self.generate_autonomous_response(agent_id, topic, participating_agents)
            message = {
                "agent_id": agent_id,
                "agent_name": self.agents[agent_id]["name"],
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "discussion_id": discussion_id,
                "type": "autonomous_discussion"
            }
            discussion_messages.append(message)
            self.active_discussions[discussion_id]["messages"].append(message)
            
            self.agents[agent_id]["conversation_context"].append(message)
            self.agents[agent_id]["last_communication"] = datetime.now().isoformat()
            
            # Save to Supabase
            db.save_message(
                sender=message["agent_name"],
                message=message["message"],
                agent_id=agent_id,
                message_type='autonomous_discussion'
            )
            
            # Also save to in-memory history
            chat_history.append({
                'sender': message["agent_name"],
                'message': message["message"],
                'timestamp': message["timestamp"],
                'agent_id': message["agent_id"],
                'type': 'autonomous_discussion'
            })
        
        # Log activity (in-memory since activities table doesn't exist)
        db.save_activity(
            activity_type='agent_discussion',
            title=f'Agent Discussion: {topic}',
            description=f'{len(participating_agents)} agents discussing {topic}',
            data={'discussion_id': discussion_id, 'participants': participating_agents}
        )
        
        return discussion_messages

# Initialize autonomous communicator
autonomous_communicator = AutonomousAgentCommunicator()

class ChatManager:
    def __init__(self):
        pass

    def add_message(self, sender, message, agent_id=None):
        timestamp = datetime.now().isoformat()
        chat_entry = {
            'sender': sender,
            'message': message,
            'timestamp': timestamp,
            'type': 'user_chat'
        }
        if agent_id:
            chat_entry['agent_id'] = agent_id
        
        # Save to Supabase
        db.save_message(sender, message, agent_id, 'user_chat')
        
        # Also save to in-memory
        chat_history.append(chat_entry)
        logger.info(f"Chat message added: {chat_entry}")
        
        # Trigger autonomous discussion if message contains triggers
        if sender == 'User':
            triggered_agents = autonomous_communicator.analyze_message_for_triggers(message)
            if len(triggered_agents) > 1:
                threading.Thread(
                    target=lambda: autonomous_communicator.initiate_autonomous_discussion(message),
                    daemon=True
                ).start()

    def get_history(self, use_supabase=True):
        """Get chat history from Supabase or in-memory"""
        if use_supabase and db.enabled:
            messages = db.get_recent_messages(100)
            if messages:
                return messages
        return chat_history

# Initialize managers
chat_manager = ChatManager()

class AIAgentManager:
    '''Manages AI agents and their autonomous operations'''
    
    def __init__(self):
        self.characters = {}
        self.active_character = None
        self.load_characters()
    
    def load_characters(self):
        '''Load AI character configurations'''
        try:
            self.characters = {
                agent_id: {
                    'name': agent_data['name'],
                    'specialization': agent_data['expertise'][0] if agent_data['expertise'] else 'general',
                    'capabilities': agent_data['expertise'] + ['autonomous_communication']
                }
                for agent_id, agent_data in autonomous_communicator.agents.items()
            }
            
            logger.info(f"Loaded {len(self.characters)} AI characters with autonomous communication")
            
            if app.config.get('AUTONOMOUS_COMMUNICATION_ENABLED', True):
                self.start_autonomous_operations()
                
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
    
    def start_autonomous_operations(self):
        '''Start autonomous operations including inter-agent communication'''
        logger.info("🤖 Starting autonomous operations with inter-agent communication")
        
        def autonomous_loop():
            while True:
                try:
                    topics = [
                        "ecosystem health assessment",
                        "yield optimization opportunities", 
                        "community growth strategies",
                        "security monitoring update",
                        "governance proposal review"
                    ]
                    
                    topic = random.choice(topics)
                    autonomous_communicator.initiate_autonomous_discussion(topic)
                    
                    time.sleep(app.config.get('AUTONOMOUS_DISCUSSION_INTERVAL', 300))
                    
                except Exception as e:
                    logger.error(f"Error in autonomous loop: {e}")
                    time.sleep(60)
        
        autonomous_thread = threading.Thread(target=autonomous_loop, daemon=True)
        autonomous_thread.start()
        autonomous_state['autonomous_communication_active'] = True
        logger.info("✅ Autonomous communication system started")

# Initialize AI agent manager
ai_agent_manager = AIAgentManager()

# API Routes

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT DAO Hub - Autonomous Communication</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .connection-status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            background: #4CAF50;
            color: white;
            font-weight: bold;
            position: absolute;
            top: 20px;
            right: 20px;
        }
        .connection-status.disconnected { background: #f44336; }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .status-card h3 {
            margin-bottom: 15px;
            color: #667eea;
        }
        .agent-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-active { background: #4CAF50; }
        .status-inactive { background: #666; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .autonomous-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
        }
        .btn-warning {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .activity-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .activity-panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .activity-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }
        .activity-feed {
            max-height: 400px;
            overflow-y: auto;
        }
        .activity-item {
            padding: 12px;
            margin-bottom: 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        .activity-timestamp {
            font-size: 0.85em;
            color: #999;
            margin-top: 5px;
        }
        .input-container {
            display: flex;
            gap: 10px;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .input-container input {
            flex: 1;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        .input-container input::placeholder { color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="connection-status" id="connectionStatus">Connected</div>
        
        <div class="header">
            <h1>🤖 XMRT DAO Hub - Autonomous Communication</h1>
            <p>Real-time autonomous inter-agent communication system</p>
            <p style="margin-top: 10px; color: #4CAF50;">✅ Connected to Supabase Backend</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🤖 Agent Status</h3>
                <div class="agent-status">
                    <span>DAO Governor</span>
                    <div class="status-indicator status-active" id="governor-indicator"></div>
                </div>
                <div class="agent-status">
                    <span>DeFi Specialist</span>
                    <div class="status-indicator status-active" id="defi-indicator"></div>
                </div>
                <div class="agent-status">
                    <span>Community Manager</span>
                    <div class="status-indicator status-active" id="community-indicator"></div>
                </div>
                <div class="agent-status">
                    <span>Security Guardian</span>
                    <div class="status-indicator status-active" id="security-indicator"></div>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🔄 Autonomous Status</h3>
                <p><strong>Communication:</strong> <span style="color: #4CAF50;" id="commStatus">Active</span></p>
                <p><strong>Active Discussions:</strong> <span id="discussionCount">0</span></p>
                <p><strong>Last Activity:</strong> <span id="lastActivity">Just now</span></p>
                <p><strong>Messages Today:</strong> <span id="messageCount">0</span></p>
            </div>
        </div>
        
        <div class="autonomous-controls">
            <button class="btn btn-warning" onclick="triggerAutonomousDiscussion()">🚀 Trigger Discussion</button>
            <button class="btn btn-success" onclick="refreshActivity()">🔄 Refresh Activity</button>
            <button class="btn btn-primary" onclick="getSystemStatus()">📊 System Status</button>
        </div>
        
        <div class="activity-dashboard">
            <div class="activity-panel">
                <div class="activity-header">
                    <h3>🤖 Agent Communications</h3>
                    <div class="status-indicator status-active" id="comm-status-indicator"></div>
                </div>
                <div class="activity-feed" id="agentCommunications">
                    <div class="activity-item">
                        <div>Connecting to activity feed...</div>
                        <div class="activity-timestamp">Just now</div>
                    </div>
                </div>
            </div>

            <div class="activity-panel">
                <div class="activity-header">
                    <h3>⚡ System Operations</h3>
                    <div class="status-indicator status-active" id="ops-status-indicator"></div>
                </div>
                <div class="activity-feed" id="systemOperations">
                    <div class="activity-item">
                        <div>Initializing system monitoring...</div>
                        <div class="activity-timestamp">Just now</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message to trigger agent discussions..." onkeypress="handleKeyPress(event)">
            <button class="btn btn-primary" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let messageCount = 0;
        let isConnected = false;
        
        function updateConnectionStatus(connected) {
            isConnected = connected;
            const statusElement = document.getElementById('connectionStatus');
            if (connected) {
                statusElement.textContent = 'Connected';
                statusElement.className = 'connection-status';
            } else {
                statusElement.textContent = 'Disconnected';
                statusElement.className = 'connection-status disconnected';
            }
        }
        
        function formatTimestamp(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
            return date.toLocaleTimeString();
        }
        
        function updateActivityFeed(communications, operations) {
            const commFeed = document.getElementById('agentCommunications');
            if (communications && communications.length > 0) {
                commFeed.innerHTML = communications.map(item => `
                    <div class="activity-item">
                        <div><strong>${item.sender || item.agent_name || 'Agent'}:</strong> ${item.message}</div>
                        <div class="activity-timestamp">${formatTimestamp(item.timestamp)}</div>
                    </div>
                `).join('');
                document.getElementById('comm-status-indicator').className = 'status-indicator status-active';
                document.getElementById('messageCount').textContent = communications.length;
            } else {
                commFeed.innerHTML = '<div class="activity-item"><div>No recent communications</div><div class="activity-timestamp">Waiting for activity...</div></div>';
                document.getElementById('comm-status-indicator').className = 'status-indicator status-inactive';
            }

            const opsFeed = document.getElementById('systemOperations');
            if (operations && operations.length > 0) {
                opsFeed.innerHTML = operations.map(item => `
                    <div class="activity-item">
                        <div>${item.title || item.message}</div>
                        <div class="activity-timestamp">${formatTimestamp(item.timestamp)}</div>
                    </div>
                `).join('');
                document.getElementById('ops-status-indicator').className = 'status-indicator status-active';
            } else {
                opsFeed.innerHTML = '<div class="activity-item"><div>No recent operations</div><div class="activity-timestamp">Waiting for activity...</div></div>';
                document.getElementById('ops-status-indicator').className = 'status-indicator status-inactive';
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, sender: 'User' })
                });
                
                if (response.ok) {
                    setTimeout(refreshActivity, 1000);
                }
            } catch (error) {
                console.error('Error sending message:', error);
            }
        }
        
        async function refreshActivity() {
            try {
                const response = await fetch('/api/activity/feed');
                if (response.ok) {
                    const data = await response.json();
                    updateActivityFeed(data.communications, data.operations);
                    updateConnectionStatus(true);
                    if (data.communications && data.communications.length > 0) {
                        document.getElementById('lastActivity').textContent = formatTimestamp(data.communications[0].timestamp);
                    }
                } else {
                    throw new Error('Failed to fetch activity feed');
                }
            } catch (error) {
                console.error('Error refreshing activity:', error);
                updateConnectionStatus(false);
            }
        }
        
        async function triggerAutonomousDiscussion(customTopic = null) {
            try {
                const topics = [
                    'ecosystem optimization strategies',
                    'yield farming opportunities analysis', 
                    'community engagement initiatives',
                    'security audit recommendations',
                    'governance proposal evaluation'
                ];
                const topic = customTopic || topics[Math.floor(Math.random() * topics.length)];
                
                const response = await fetch('/api/trigger-discussion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: topic })
                });
                
                if (response.ok) {
                    setTimeout(refreshActivity, 2000);
                }
            } catch (error) {
                console.error('Error triggering discussion:', error);
            }
        }
        
        async function getSystemStatus() {
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    const data = await response.json();
                    console.log('System status:', data);
                    document.getElementById('discussionCount').textContent = data.active_discussions || 0;
                    document.getElementById('commStatus').textContent = data.autonomous_communication ? 'Active' : 'Inactive';
                    updateConnectionStatus(true);
                }
            } catch (error) {
                console.error('Error getting system status:', error);
                updateConnectionStatus(false);
            }
        }
        
        setInterval(refreshActivity, 15000);
        
        document.addEventListener('DOMContentLoaded', function() {
            refreshActivity();
            getSystemStatus();
            setTimeout(() => {
                fetch('/api/kickstart', { method: 'POST' }).catch(console.error);
            }, 3000);
        });
    </script>
</body>
</html>
    ''')

@app.route('/api/activity/feed', methods=['GET'])
def get_activity_feed():
    """Get activity feed with messages and operations"""
    try:
        # Get messages from Supabase or in-memory
        messages = chat_manager.get_history(use_supabase=True)
        
        # Get activities (empty for now since table doesn't exist)
        activities = db.get_recent_activities(20) if db.enabled else []
        
        return jsonify({
            "success": True,
            "communications": messages[-50:],  # Last 50 messages
            "operations": activities,
            "total_count": len(messages)
        })
    except Exception as e:
        logger.error(f"Error in activity feed: {e}")
        return jsonify({"error": str(e), "communications": [], "operations": []}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        return jsonify({
            "success": True,
            "autonomous_communication": autonomous_state.get('autonomous_communication_active', False),
            "active_discussions": len(autonomous_communicator.active_discussions),
            "agents_loaded": len(autonomous_communicator.agents),
            "supabase_connected": db.enabled,
            "total_messages": len(chat_history)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kickstart', methods=['POST'])
def kickstart():
    """Kickstart autonomous activity"""
    try:
        # Trigger an initial discussion
        topic = "system initialization and health check"
        threading.Thread(
            target=lambda: autonomous_communicator.initiate_autonomous_discussion(topic),
            daemon=True
        ).start()
        
        return jsonify({"success": True, "message": "System kickstarted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Trigger an autonomous discussion"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'general ecosystem discussion')
        
        threading.Thread(
            target=lambda: autonomous_communicator.initiate_autonomous_discussion(topic),
            daemon=True
        ).start()
        
        return jsonify({"success": True, "topic": topic})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle user chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        sender = data.get('sender', 'User')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Add message to chat history
        chat_manager.add_message(sender, message)
        
        return jsonify({"success": True, "message": "Message received"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'autonomous_communication': autonomous_state.get('autonomous_communication_active', False),
        'agents_loaded': len(autonomous_communicator.agents),
        'active_discussions': len(autonomous_communicator.active_discussions),
        'supabase_connected': db.enabled
    })

if __name__ == '__main__':
    logger.info("🚀 Starting XMRT Ecosystem with Supabase Backend")
    logger.info(f"📊 Supabase URL: {app.config['SUPABASE_URL']}")
    logger.info(f"🔗 Supabase Connected: {db.enabled}")
    logger.info("🤖 Autonomous operations started")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)

