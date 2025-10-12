"""
XMRT Ecosystem - Enhanced Chat Messages Handler
Fixes Supabase schema issues and provides robust error handling
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class EnhancedChatHandler:
    """Enhanced chat message handler with schema error recovery"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.backup_messages: List[Dict] = []
        self._verify_schema()
    
    def _verify_schema(self) -> bool:
        """Verify that the chat_messages table has the required schema"""
        try:
            # Test insert with expected schema
            test_data = {
                'content': 'schema_test',
                'sender': 'system',
                'type': 'test',
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('chat_messages').insert(test_data).execute()
            
            if result.data:
                # Clean up test data
                self.supabase.table('chat_messages').delete().eq('content', 'schema_test').execute()
                logger.info("✅ Chat messages schema verification passed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Schema verification failed: {e}")
            logger.error("Please run the SQL migration to fix the schema")
            return False
    
    def save_message(self, message_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Save message with robust error handling and fallback
        
        Args:
            message_data: Dictionary containing message information
            
        Returns:
            Result from Supabase or None if failed
        """
        try:
            # Ensure required fields
            processed_data = self._process_message_data(message_data)
            
            # Attempt to save to Supabase
            result = self.supabase.table('chat_messages').insert(processed_data).execute()
            
            if result.data:
                logger.info(f"✅ Message saved to Supabase: {processed_data.get('type', 'unknown')}")
                return result.data[0]
            else:
                logger.warning("⚠️ No data returned from Supabase insert")
                self._backup_message(processed_data)
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving message to Supabase: {e}")
            
            # Check if it's the schema error we're trying to fix
            if "Could not find the 'content' column" in str(e):
                logger.error("🔧 SCHEMA FIX NEEDED: Run the SQL migration to add the content column")
            
            # Backup the message
            self._backup_message(message_data)
            return None
    
    def _process_message_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize message data"""
        processed = data.copy()
        
        # Ensure content field exists
        if 'content' not in processed:
            if 'message' in processed:
                processed['content'] = processed['message']
            else:
                processed['content'] = processed.get('text', '')
        
        # Ensure message field for compatibility
        if 'message' not in processed:
            processed['message'] = processed.get('content', '')
        
        # Add timestamp if missing
        if 'timestamp' not in processed:
            processed['timestamp'] = datetime.now().isoformat()
        
        # Ensure required fields have defaults
        processed.setdefault('sender', 'unknown')
        processed.setdefault('type', 'user_chat')
        
        return processed
    
    def _backup_message(self, message_data: Dict[str, Any]):
        """Backup message to memory and file when database fails"""
        self.backup_messages.append({
            'data': message_data,
            'timestamp': datetime.now().isoformat(),
            'error_time': datetime.now().isoformat()
        })
        
        # Also save to file for persistence
        try:
            backup_file = 'chat_messages_backup.jsonl'
            with open(backup_file, 'a') as f:
                f.write(json.dumps({
                    'data': message_data,
                    'backup_time': datetime.now().isoformat()
                }) + '\n')
                
            logger.info(f"💾 Message backed up to {backup_file}")
        except Exception as e:
            logger.error(f"Failed to backup to file: {e}")
    
    def save_activity(self, activity_data: Dict[str, Any]) -> Optional[Dict]:
        """Save activity to feed with error handling"""
        try:
            processed_activity = {
                'type': activity_data.get('type', 'unknown'),
                'title': activity_data.get('title', 'Untitled Activity'),
                'description': activity_data.get('description', ''),
                'data': activity_data.get('data', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('activity_feed').insert(processed_activity).execute()
            
            if result.data:
                logger.info(f"✅ Activity saved: {processed_activity['type']}")
                return result.data[0]
            else:
                logger.warning("⚠️ No data returned from activity insert")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving activity: {e}")
            return None
    
    def get_backup_messages(self) -> List[Dict]:
        """Get messages that were backed up due to database errors"""
        return self.backup_messages.copy()
    
    def retry_backup_messages(self) -> int:
        """Retry saving backed up messages after schema is fixed"""
        if not self.backup_messages:
            return 0
        
        success_count = 0
        failed_messages = []
        
        for backup_msg in self.backup_messages:
            result = self.save_message(backup_msg['data'])
            if result:
                success_count += 1
            else:
                failed_messages.append(backup_msg)
        
        # Update backup list with only failed messages
        self.backup_messages = failed_messages
        
        if success_count > 0:
            logger.info(f"✅ Successfully restored {success_count} backed up messages")
        
        return success_count

# Usage example:
# chat_handler = EnhancedChatHandler(supabase_url, supabase_key)
# result = chat_handler.save_message({'content': 'Hello', 'sender': 'user', 'type': 'user_chat'})
