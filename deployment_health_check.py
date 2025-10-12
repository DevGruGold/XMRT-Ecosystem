#!/usr/bin/env python3
"""
XMRT-Ecosystem Deployment Health Check
"""

import requests
import sys
import time
import json
from datetime import datetime

def check_deployment_health(base_url="https://xmrt-ecosystem-1-rup6.onrender.com"):
    """Check if the deployment is healthy"""
    
    print(f"🔍 Checking deployment health for: {base_url}")
    
    endpoints = [
        {"path": "/", "name": "Main Application"},
        {"path": "/health", "name": "Health Check"},
        {"path": "/api/status", "name": "API Status"}
    ]
    
    results = []
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint['path']}"
        
        try:
            print(f"  Testing {endpoint['name']}: {url}")
            response = requests.get(url, timeout=30)
            
            status = {
                "endpoint": endpoint["name"],
                "url": url,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                print(f"    ✅ Success ({response.status_code}) - {response.elapsed.total_seconds():.2f}s")
                try:
                    # Try to parse JSON response
                    json_data = response.json()
                    status["response_data"] = json_data
                    print(f"    📊 JSON Response: {json.dumps(json_data, indent=2)[:200]}...")
                except:
                    # Plain text response
                    status["response_text"] = response.text[:200]
                    print(f"    📄 Text Response: {response.text[:100]}...")
            else:
                print(f"    ❌ Failed ({response.status_code})")
                status["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            print(f"    ⏱️  Timeout (>30s)")
            status = {
                "endpoint": endpoint["name"],
                "url": url,
                "success": False,
                "error": "Timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            status = {
                "endpoint": endpoint["name"],
                "url": url,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        results.append(status)
        time.sleep(1)  # Brief pause between requests
    
    # Summary
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"\n📊 Health Check Summary:")
    print(f"  ✅ Successful: {successful}/{total}")
    print(f"  ❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print(f"  🎉 All endpoints healthy!")
        return True
    else:
        print(f"  ⚠️  Some endpoints need attention")
        return False

def check_render_service_status():
    """Check Render service status via API if possible"""
    
    print(f"\n🔍 Checking Render service status...")
    
    # This would require Render API access, for now just check the public URL
    service_url = "https://xmrt-ecosystem-1-rup6.onrender.com"
    
    try:
        response = requests.get(service_url, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ Service is responding")
            return True
        else:
            print(f"  ⚠️  Service returned {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Service not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🏥 XMRT-Ecosystem Deployment Health Check")
    print("=" * 50)
    
    # Run health checks
    deployment_healthy = check_deployment_health()
    service_healthy = check_render_service_status()
    
    print(f"\n🎯 Overall Status:")
    if deployment_healthy and service_healthy:
        print(f"  ✅ Deployment is healthy and operational")
        sys.exit(0)
    else:
        print(f"  ⚠️  Deployment needs attention")
        sys.exit(1)
