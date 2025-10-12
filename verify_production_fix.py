#!/usr/bin/env python3
"""
Verification script for XMRT Ecosystem fix
Tests all endpoints and functionality
"""

import requests
import time
import json

def test_production_service():
    """Test the production service after fix deployment"""
    
    base_url = "https://xmrt-ecosystem-python-service.onrender.com"
    print(f"🧪 Testing XMRT Ecosystem at {base_url}")
    print("=" * 60)
    
    tests = [
        {
            'name': 'Service Health Check',
            'method': 'GET',
            'url': f'{base_url}/api/status',
            'expect_json': True
        },
        {
            'name': 'Chat Messages Endpoint',
            'method': 'GET', 
            'url': f'{base_url}/api/chat/messages',
            'expect_json': True
        },
        {
            'name': 'Send Test Message',
            'method': 'POST',
            'url': f'{base_url}/api/chat',
            'data': {'message': 'Test message - fix verification'},
            'expect_json': True
        },
        {
            'name': 'Activity Feed',
            'method': 'GET',
            'url': f'{base_url}/api/activity/feed', 
            'expect_json': True
        },
        {
            'name': 'Trigger Agent Discussion',
            'method': 'POST',
            'url': f'{base_url}/api/trigger-discussion',
            'expect_json': True
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"Testing: {test['name']}...")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:
                data = test.get('data', {})
                response = requests.post(
                    test['url'], 
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            success = 200 <= response.status_code < 300
            
            if success:
                print(f"  ✅ PASSED - Status: {response.status_code}")
                if test.get('expect_json'):
                    try:
                        data = response.json()
                        print(f"     Response: {str(data)[:100]}...")
                    except:
                        print(f"     Response: {response.text[:100]}...")
            else:
                print(f"  ❌ FAILED - Status: {response.status_code}")
                print(f"     Error: {response.text[:200]}")
            
            results.append({
                'test': test['name'],
                'success': success,
                'status': response.status_code
            })
            
            time.sleep(1)  # Small delay between tests
            
        except Exception as e:
            print(f"  ❌ ERROR - {str(e)}")
            results.append({
                'test': test['name'],
                'success': False,
                'error': str(e)
            })
    
    # Test chat flow specifically
    print(f"\n💬 Testing Complete Chat Flow...")
    
    try:
        # Send a message
        response = requests.post(
            f'{base_url}/api/chat',
            json={'message': 'Hello agents, this is a test!'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("  ✅ User message sent successfully")
            
            # Wait for processing
            time.sleep(3)
            
            # Check for messages
            messages_response = requests.get(f'{base_url}/api/chat/messages', timeout=10)
            
            if messages_response.status_code == 200:
                messages = messages_response.json()
                print(f"  ✅ Retrieved {len(messages)} messages")
                
                # Look for our test message and agent responses
                test_messages = [m for m in messages if 'test' in m.get('content', '').lower()]
                agent_messages = [m for m in messages if 'XMRT' in m.get('sender', '')]
                
                print(f"  📝 Test messages found: {len(test_messages)}")
                print(f"  🤖 Agent messages found: {len(agent_messages)}")
                
                if agent_messages:
                    latest_agent = agent_messages[-1]
                    print(f"  ✅ Latest agent response: {latest_agent['content'][:80]}...")
                    print("  🎉 CHAT FLOW WORKING!")
                else:
                    print("  ⚠️ No agent responses found")
                    
            else:
                print(f"  ❌ Failed to retrieve messages: {messages_response.status_code}")
        else:
            print(f"  ❌ Failed to send message: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Chat flow test error: {e}")
    
    # Summary
    passed = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your XMRT Ecosystem is working correctly!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed - system is functional")
    else:
        print("⚠️ Multiple test failures - needs attention")
    
    return results

if __name__ == "__main__":
    print("🚀 XMRT Ecosystem Fix Verification")
    print("Testing production deployment...")
    print("")
    
    results = test_production_service()
    
    print("\n🔗 Next Steps:")
    print("1. Visit: https://xmrt-ecosystem-python-service.onrender.com/")
    print("2. Test the chat interface manually")
    print("3. Verify agents respond to your messages")
    print("4. Check that conversations flow naturally")
