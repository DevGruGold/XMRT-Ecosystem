#!/usr/bin/env python3
"""
Quick Test Script for XMRT Ecosystem Supabase Fix
Tests the exact API payload format that should work
"""

import requests
import json
from datetime import datetime

def test_supabase_api():
    """Test the Supabase API directly with the exact payload format"""
    
    # Your Supabase details
    SUPABASE_URL = "https://vawouugtzwmejxqkeqqj.supabase.co"
    # You'll need your actual anon key - get it from Supabase dashboard
    SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY_HERE"
    
    # API endpoint
    url = f"{SUPABASE_URL}/rest/v1/chat_messages"
    
    # Headers
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Test payload - exactly what should work now
    test_payload = {
        "sender": "User",
        "content": "Hello world!",
        "type": "user_chat"
    }
    
    print("🧪 Testing Supabase API with minimal payload...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=test_payload)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Message saved successfully!")
            print(f"Response: {response.json()}")
        else:
            print("❌ FAILED!")
            print(f"Error Response: {response.text}")
            
            if response.status_code == 400:
                error_data = response.json()
                if "Could not find the 'content' column" in error_data.get('message', ''):
                    print("\n🔧 DIAGNOSIS: The content column is still missing!")
                    print("   Please run the SQL migration in your Supabase dashboard.")
                elif "sender" in error_data.get('message', ''):
                    print("\n🔧 DIAGNOSIS: The sender column configuration issue!")
                    print("   Check that sender column exists and is properly configured.")
                    
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Check your Supabase URL and API key")

def test_with_message_field():
    """Test backward compatibility - using 'message' instead of 'content'"""
    
    SUPABASE_URL = "https://vawouugtzwmejxqkeqqj.supabase.co"
    SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY_HERE"
    
    url = f"{SUPABASE_URL}/rest/v1/chat_messages"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Test with 'message' field instead of 'content' (should work with trigger)
    test_payload = {
        "sender": "User",
        "message": "Test with message field",
        "type": "user_chat"
    }
    
    print("\n🧪 Testing backward compatibility with 'message' field...")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=test_payload)
        
        if response.status_code == 201:
            print("✅ SUCCESS! Backward compatibility works!")
            result = response.json()
            print(f"Content field populated: {result[0].get('content')}")
            print(f"Message field: {result[0].get('message')}")
        else:
            print("❌ Backward compatibility failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_table_schema():
    """Check the current table schema"""
    
    SUPABASE_URL = "https://vawouugtzwmejxqkeqqj.supabase.co"
    SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY_HERE"
    
    # Query to get table schema
    url = f"{SUPABASE_URL}/rest/v1/rpc/check_schema"
    
    print("\n🔍 Checking table schema...")
    print("Note: This requires a custom RPC function to be created in Supabase")
    
    # Alternative: try to insert and see what error we get
    url = f"{SUPABASE_URL}/rest/v1/chat_messages"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    # Deliberately incomplete payload to see schema requirements
    test_payload = {"sender": "Test"}
    
    try:
        response = requests.post(url, headers=headers, json=test_payload)
        print(f"Schema probe response: {response.status_code}")
        if response.status_code != 201:
            error = response.json()
            print(f"Error reveals schema requirements: {error}")
    except Exception as e:
        print(f"Schema check error: {e}")

def generate_sql_test():
    """Generate SQL commands to test the fix"""
    
    sql_commands = """
-- Test commands to run in Supabase SQL Editor after migration

-- 1. Check table exists and has correct columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
ORDER BY ordinal_position;

-- 2. Test minimal required insert
INSERT INTO chat_messages (sender, content, type) 
VALUES ('User', 'Hello world!', 'user_chat');

-- 3. Test backward compatibility with message field
INSERT INTO chat_messages (sender, message, type) 
VALUES ('System', 'Test message field', 'system');

-- 4. Verify both inserts worked and trigger functioned
SELECT id, sender, content, message, type, timestamp 
FROM chat_messages 
ORDER BY timestamp DESC 
LIMIT 5;

-- 5. Clean up test data
DELETE FROM chat_messages WHERE content IN ('Hello world!', 'Test message field');

-- 6. Test that required fields are enforced
-- This should fail:
-- INSERT INTO chat_messages (content, type) VALUES ('No sender', 'user_chat');
"""

    print("\n📋 SQL Test Commands:")
    print("Copy these commands and run in your Supabase SQL Editor:")
    print("=" * 60)
    print(sql_commands)

if __name__ == "__main__":
    print("🔧 XMRT Ecosystem Supabase Fix - Test Suite")
    print("=" * 50)
    
    print("\n⚠️  IMPORTANT: Update SUPABASE_ANON_KEY in this script first!")
    print("Get your anon key from: https://vawouugtzwmejxqkeqqj.supabase.co/project/settings/api")
    
    # Generate SQL test commands
    generate_sql_test()
    
    # Uncomment these after adding your API key:
    # test_supabase_api()
    # test_with_message_field()
    # check_table_schema()
    
    print("\n🎯 Next Steps:")
    print("1. Add your Supabase anon key to this script")
    print("2. Run the SQL migration in Supabase dashboard")  
    print("3. Uncomment and run the API tests")
    print("4. Update your service code with the new payload format")