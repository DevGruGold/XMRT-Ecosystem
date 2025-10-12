#!/usr/bin/env python3
"""
XMRT Ecosystem - Fixed Service Main Code
Ensures all messages have proper sender field and adds frontend API endpoints
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from supabase import create_client, Client

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL', 'https://vawouugtzwmejxqkeqqj.supabase.co')
supabase_key = os.getenv('SUPABASE_ANON_KEY', 'your-key-here')
supabase: Client = create_client(supabase_url, supabase_key)

# Agent configurations
AGENTS = {
    'defi_specialist': 'XMRT DeFi Specialist',
    'community_manager': 'XMRT Community Manager',
    'security_guardian': 'XMRT Security Guardian',
    'governance_lead': 'XMRT Governance Lead'
}

def save_message_to_supabase(sender, content, msg_type='user_chat', metadata=None):
    """
    FIXED: Always ensure sender, content, and type are provided
    """
    if not sender or not sender.strip():
        sender = 'System'  # Fallback sender
    
    if not content or not content.strip():
        content = '[Empty message]'  # Fallback content
    
    message_data = {
        'sender': sender.strip(),
        'content': content.strip(),
        'type': msg_type,
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata or {}
    }
    
    try:
        result = supabase.table('chat_messages').insert(message_data).execute()
        if result.data:
            logger.info(f"✅ Message saved to Supabase: {sender}")
            return result.data[0]
        else:
            logger.warning(f"⚠️ No data returned for message from {sender}")
            return None
    except Exception as e:
        logger.error(f"❌ Error saving message to Supabase: {e}")
        return None

def save_activity_to_supabase(activity_type, title, description="", data=None):
    """
    Save activity to activity feed (separate from chat messages)
    """
    activity_data = {
        'type': activity_type,
        'title': title,
        'description': description,
        'data': data or {},
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('activity_feed').insert(activity_data).execute()
        if result.data:
            logger.info(f"✅ Activity saved: {activity_type}")
            return result.data[0]
        else:
            logger.warning(f"⚠️ No data returned for activity: {activity_type}")
            return None
    except Exception as e:
        logger.error(f"❌ Error saving activity: {e}")
        return None

def log_agent_discussion(topic, agent_name=None):
    """
    FIXED: Log agent discussion with proper sender
    """
    if not agent_name:
        agent_name = 'XMRT Community Manager'  # Default agent
    
    # Save as chat message
    message_result = save_message_to_supabase(
        sender=agent_name,
        content=f"Initiating discussion on: {topic}",
        msg_type='agent_discussion',
        metadata={'topic': topic, 'discussion_type': 'autonomous'}
    )
    
    # Save as activity
    activity_result = save_activity_to_supabase(
        activity_type='agent_discussion',
        title=f'Agent Discussion: {topic}',
        description=f'Autonomous discussion initiated by {agent_name}',
        data={'topic': topic, 'agent': agent_name}
    )
    
    return message_result, activity_result

def generate_agent_response(user_message, agent_name='XMRT Community Manager'):
    """
    FIXED: Generate agent response with proper sender
    """
    # Simple response generation (replace with your AI logic)
    responses = {
        'XMRT Community Manager': f"Hello! I'm here to help with community matters. You said: '{user_message}'. How can I assist you further?",
        'XMRT DeFi Specialist': f"Thanks for your message about: '{user_message}'. Let me provide some DeFi insights...",
        'XMRT Security Guardian': f"Security check: Your message '{user_message}' has been reviewed. All systems secure.",
        'XMRT Governance Lead': f"Governance consideration for: '{user_message}'. Let's discuss the implications..."
    }
    
    response_content = responses.get(agent_name, f"Agent response to: '{user_message}'")
    
    # Save agent response
    return save_message_to_supabase(
        sender=agent_name,
        content=response_content,
        msg_type='agent_response',
        metadata={'responding_to': user_message}
    )

# API ENDPOINTS

@app.route('/')
def index():
    """Serve the main page with integrated chat"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XMRT Ecosystem</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 800px; margin: 0 auto; }
            .chat-container { border: 1px solid #333; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; background: #2a2a2a; }
            .message { margin: 10px 0; padding: 8px; border-radius: 8px; }
            .message.user { background: #0066cc; text-align: right; }
            .message.xmrt-community-manager,
            .message.xmrt-defi-specialist,
            .message.xmrt-security-guardian,
            .message.xmrt-governance-lead { background: #006600; }
            .message.system { background: #660066; }
            .sender { font-weight: bold; font-size: 0.9em; }
            .timestamp { font-size: 0.8em; opacity: 0.7; }
            input[type="text"] { width: 70%; padding: 8px; }
            button { padding: 8px 16px; margin-left: 10px; }
            .status { margin: 10px 0; padding: 8px; background: #333; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 XMRT Ecosystem</h1>
            <div class="status">Status: <span id="status">Connecting...</span></div>
            
            <div id="chat-messages" class="chat-container">
                <div class="message system">
                    <div class="sender">System</div>
                    <div>Welcome to XMRT Ecosystem! Type a message to interact with AI agents.</div>
                </div>
            </div>
            
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
            <button onclick="triggerDiscussion()">Trigger Discussion</button>
            <button onclick="fetchMessages()">Refresh</button>
        </div>
        
        <script>
            async function fetchMessages() {
                try {
                    const response = await fetch('/api/chat/messages');
                    const messages = await response.json();
                    
                    const container = document.getElementById('chat-messages');
                    container.innerHTML = '';
                    
                    messages.forEach(msg => {
                        const div = document.createElement('div');
                        const senderClass = msg.sender.toLowerCase().replace(/\\s+/g, '-');
                        div.className = `message ${senderClass}`;
                        div.innerHTML = `
                            <div class="sender">${msg.sender}</div>
                            <div>${msg.content}</div>
                            <div class="timestamp">${new Date(msg.timestamp).toLocaleTimeString()}</div>
                        `;
                        container.appendChild(div);
                    });
                    
                    container.scrollTop = container.scrollHeight;
                    document.getElementById('status').textContent = `Connected - ${messages.length} messages`;
                } catch (error) {
                    console.error('Error fetching messages:', error);
                    document.getElementById('status').textContent = 'Error loading messages';
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    if (response.ok) {
                        input.value = '';
                        setTimeout(fetchMessages, 500); // Refresh after sending
                    } else {
                        alert('Failed to send message');
                    }
                } catch (error) {
                    console.error('Error sending message:', error);
                    alert('Error sending message');
                }
            }
            
            async function triggerDiscussion() {
                try {
                    const response = await fetch('/api/trigger-discussion', { method: 'POST' });
                    if (response.ok) {
                        setTimeout(fetchMessages, 1000);
                    }
                } catch (error) {
                    console.error('Error triggering discussion:', error);
                }
            }
            
            // Auto-refresh every 3 seconds
            setInterval(fetchMessages, 3000);
            
            // Initial load
            fetchMessages();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    """
    NEW: Fetch recent chat messages for frontend display
    """
    try:
        result = supabase.table('chat_messages')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(50)\
            .execute()
        
        if result.data:
            # Reverse to show oldest first
            messages = list(reversed(result.data))
            return jsonify(messages), 200
        else:
            return jsonify([]), 200
            
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """
    FIXED: Handle user chat with proper sender field
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Save user message with proper sender
        user_result = save_message_to_supabase(
            sender='User',
            content=user_message,
            msg_type='user_chat'
        )
        
        if user_result:
            logger.info(f"✅ User message saved: {user_message}")
            
            # Generate agent response
            import random
            agent_name = random.choice(list(AGENTS.values()))
            agent_result = generate_agent_response(user_message, agent_name)
            
            if agent_result:
                logger.info(f"✅ Agent response generated: {agent_name}")
            
            return jsonify({
                'status': 'success',
                'user_message': user_result,
                'agent_response': agent_result
            }), 200
        else:
            return jsonify({'error': 'Failed to save message'}), 500
            
    except Exception as e:
        logger.error(f"Error in chat handler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """
    FIXED: Trigger agent discussion with proper sender
    """
    try:
        import random
        topics = [
            'yield farming opportunities analysis',
            'community engagement initiatives', 
            'governance proposal review',
            'security assessment update',
            'ecosystem development planning'
        ]
        
        topic = random.choice(topics)
        agent_name = random.choice(list(AGENTS.values()))
        
        message_result, activity_result = log_agent_discussion(topic, agent_name)
        
        if message_result:
            logger.info(f"🤖 Autonomous discussion triggered: {topic}")
            return jsonify({
                'status': 'success',
                'topic': topic,
                'agent': agent_name,
                'message': message_result,
                'activity': activity_result
            }), 200
        else:
            return jsonify({'error': 'Failed to trigger discussion'}), 500
            
    except Exception as e:
        logger.error(f"Error triggering discussion: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kickstart', methods=['POST'])
def kickstart():
    """
    FIXED: Kickstart system with proper sender
    """
    try:
        agent_name = 'XMRT Community Manager'
        topic = 'system initialization and health check'
        
        message_result, activity_result = log_agent_discussion(topic, agent_name)
        
        if message_result:
            logger.info(f"🤖 System kickstarted: {topic}")
            return jsonify({
                'status': 'success',
                'topic': topic,
                'agent': agent_name,
                'message': message_result,
                'activity': activity_result
            }), 200
        else:
            return jsonify({'error': 'Failed to kickstart system'}), 500
            
    except Exception as e:
        logger.error(f"Error in kickstart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity/feed', methods=['GET'])
def get_activity_feed():
    """Get recent activities"""
    try:
        result = supabase.table('activity_feed')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(20)\
            .execute()
        
        return jsonify(result.data or []), 200
        
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Test Supabase connection
        result = supabase.table('chat_messages').select('id').limit(1).execute()
        
        return jsonify({
            'status': 'online',
            'supabase_connected': True,
            'agents_active': len(AGENTS),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'status': 'error',
            'supabase_connected': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting XMRT Ecosystem with fixed sender handling")
    logger.info(f"📊 Supabase URL: {supabase_url}")
    
    # Test connection
    try:
        test_result = supabase.table('chat_messages').select('id').limit(1).execute()
        logger.info("✅ Supabase connection successful")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
    
    # Start autonomous operations
    import threading
    import time
    
    def autonomous_operations():
        """Background task for autonomous operations"""
        while True:
            try:
                time.sleep(300)  # Every 5 minutes
                import random
                if random.random() < 0.3:  # 30% chance
                    topic = random.choice([
                        'market analysis update',
                        'community growth metrics',
                        'security patrol report'
                    ])
                    agent = random.choice(list(AGENTS.values()))
                    log_agent_discussion(topic, agent)
                    
            except Exception as e:
                logger.error(f"Error in autonomous operations: {e}")
    
    # Start background thread
    bg_thread = threading.Thread(target=autonomous_operations, daemon=True)
    bg_thread.start()
    logger.info("✅ Autonomous operations started")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=10000, debug=False)