"""
Updated Python Service Code for XMRT Ecosystem
Ensures proper payload format for Supabase chat_messages API
Minimal required fields: sender, content, type
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class XMRTChatHandler:
    """
    Updated chat handler that sends correct payload format to Supabase
    Ensures sender, content, and type are always included
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.backup_messages: List[Dict] = []
        
    def save_message(self, message_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Save message with correct payload format for Supabase API
        
        Required fields in payload:
        - sender: string (required) - "User", "System", "Agent", etc.
        - content: string (required) - the message content  
        - type: string (optional, defaults to "user_chat")
        
        Args:
            message_data: Dictionary containing message information
            
        Returns:
            Result from Supabase or None if failed
        """
        try:
            # Create payload with required fields
            payload = self._create_supabase_payload(message_data)
            
            # Validate payload meets API requirements
            self._validate_payload(payload)
            
            # Send to Supabase with correct format
            result = self.supabase.table('chat_messages').insert(payload).execute()
            
            if result.data:
                logger.info(f"✅ Message saved to Supabase: {payload.get('sender')} - {payload.get('type')}")
                return result.data[0]
            else:
                logger.warning("⚠️ No data returned from Supabase insert")
                self._backup_message(payload)
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving message to Supabase: {e}")
            
            # Specific error handling for schema issues
            if "Could not find the 'content' column" in str(e):
                logger.error("🔧 SCHEMA ERROR: Run the SQL migration to add content column!")
            elif "sender" in str(e).lower() and "not null" in str(e).lower():
                logger.error("🔧 PAYLOAD ERROR: sender field is required!")
            
            self._backup_message(message_data)
            return None
    
    def _create_supabase_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create properly formatted payload for Supabase API
        
        Minimal JSON that will pass:
        { "sender": "User", "content": "Hello world!", "type": "user_chat" }
        """
        payload = {}
        
        # 1. REQUIRED: sender field
        sender = data.get('sender') or data.get('from') or data.get('user') or 'Unknown'
        if not sender or not sender.strip():
            sender = 'System'  # Fallback to avoid empty sender
        payload['sender'] = sender.strip()
        
        # 2. REQUIRED: content field
        content = data.get('content') or data.get('message') or data.get('text') or ''
        if not content or not content.strip():
            content = '[Empty message]'  # Fallback for empty content
        payload['content'] = content.strip()
        
        # 3. OPTIONAL: type field (defaults to 'user_chat')
        message_type = data.get('type') or 'user_chat'
        payload['type'] = message_type
        
        # 4. OPTIONAL: Add other fields if present
        if 'timestamp' in data:
            payload['timestamp'] = data['timestamp']
        else:
            payload['timestamp'] = datetime.now().isoformat()
            
        if 'session_id' in data:
            payload['session_id'] = data['session_id']
            
        if 'thread_id' in data:
            payload['thread_id'] = data['thread_id']
            
        if 'metadata' in data:
            payload['metadata'] = data['metadata']
        
        # For backward compatibility, also include message field
        payload['message'] = payload['content']
        
        return payload
    
    def _validate_payload(self, payload: Dict[str, Any]) -> None:
        """Validate that payload meets Supabase API requirements"""
        
        # Check required fields
        if 'sender' not in payload or not payload['sender'].strip():
            raise ValueError("sender is required and cannot be empty")
            
        if 'content' not in payload or not payload['content'].strip():
            raise ValueError("content is required and cannot be empty")
            
        if 'type' not in payload:
            raise ValueError("type is required")
    
    def _backup_message(self, message_data: Dict[str, Any]):
        """Backup message when Supabase fails"""
        self.backup_messages.append({
            'data': message_data,
            'timestamp': datetime.now().isoformat(),
            'error_time': datetime.now().isoformat()
        })
        
        # Also save to file
        try:
            with open('chat_backup.jsonl', 'a') as f:
                f.write(json.dumps({
                    'data': message_data,
                    'backup_time': datetime.now().isoformat()
                }) + '\n')
        except Exception as e:
            logger.error(f"Failed to backup to file: {e}")
    
    def save_activity(self, activity_data: Dict[str, Any]) -> Optional[Dict]:
        """Save activity to feed"""
        try:
            payload = {
                'type': activity_data.get('type', 'unknown'),
                'title': activity_data.get('title', 'Untitled Activity'),
                'description': activity_data.get('description', ''),
                'data': activity_data.get('data', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('activity_feed').insert(payload).execute()
            
            if result.data:
                logger.info(f"✅ Activity saved: {payload['type']}")
                return result.data[0]
                
        except Exception as e:
            logger.error(f"❌ Error saving activity: {e}")
            
        return None

# Example usage functions matching your current service patterns

def save_user_message(chat_handler: XMRTChatHandler, message: str, user: str = "User") -> bool:
    """Save a user chat message with proper format"""
    message_data = {
        'sender': user,
        'content': message,
        'type': 'user_chat'
    }
    result = chat_handler.save_message(message_data)
    return result is not None

def save_agent_response(chat_handler: XMRTChatHandler, response: str, agent_name: str = "Agent") -> bool:
    """Save an agent response with proper format"""
    message_data = {
        'sender': agent_name,
        'content': response,
        'type': 'agent_response'
    }
    result = chat_handler.save_message(message_data)
    return result is not None

def save_system_message(chat_handler: XMRTChatHandler, message: str, msg_type: str = "system") -> bool:
    """Save a system message with proper format"""
    message_data = {
        'sender': 'System',
        'content': message,
        'type': msg_type
    }
    result = chat_handler.save_message(message_data)
    return result is not None

def log_agent_discussion(chat_handler: XMRTChatHandler, topic: str) -> bool:
    """Log an agent discussion activity"""
    activity_data = {
        'type': 'agent_discussion',
        'title': f'Agent Discussion: {topic}',
        'description': f'Autonomous discussion initiated on topic: {topic}',
        'data': {'topic': topic}
    }
    result = chat_handler.save_activity(activity_data)
    return result is not None

# Integration example for your existing service
def integrate_with_existing_service():
    """
    Example of how to integrate this with your existing service_main.py
    Replace your current Supabase chat message saves with this pattern:
    """
    
    # Initialize (replace your current Supabase setup)
    supabase_url = os.getenv('SUPABASE_URL', 'https://vawouugtzwmejxqkeqqj.supabase.co')
    supabase_key = os.getenv('SUPABASE_ANON_KEY', 'your-key-here')
    
    chat_handler = XMRTChatHandler(supabase_url, supabase_key)
    
    # Example 1: Handle user chat (from /api/chat endpoint)
    def handle_user_chat(message: str, user_id: str = "User"):
        success = save_user_message(chat_handler, message, user_id)
        if success:
            # Trigger agent response here
            # agent_response = generate_agent_response(message)
            # save_agent_response(chat_handler, agent_response)
            pass
        return success
    
    # Example 2: Handle autonomous discussions (from your trigger endpoints)
    def trigger_discussion(topic: str):
        success = log_agent_discussion(chat_handler, topic)
        if success:
            # Your existing agent logic here
            pass
        return success
    
    return chat_handler

if __name__ == "__main__":
    # Test the handler
    import os
    
    # Use your actual Supabase credentials
    supabase_url = "https://vawouugtzwmejxqkeqqj.supabase.co"
    supabase_key = "your-anon-key-here"  # Replace with actual key
    
    handler = XMRTChatHandler(supabase_url, supabase_key)
    
    # Test with minimal required payload
    test_result = handler.save_message({
        "sender": "User",
        "content": "Hello world!",
        "type": "user_chat"
    })
    
    if test_result:
        print("✅ Test message saved successfully!")
        print(f"Saved message ID: {test_result.get('id')}")
    else:
        print("❌ Test failed - check your Supabase credentials and schema")