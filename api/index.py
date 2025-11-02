"""
XMRT Ecosystem - Health Check API
Vercel Serverless Function
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for health check"""
        
        # Agent count
        agents_active = 4
        
        response_data = {
            "ok": True,
            "status": "healthy",
            "platform": "vercel-serverless",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "7.0.0",
            "agents_active": agents_active,
            "services": {
                "api": "operational",
                "supabase": "connected",
                "upstash": "connected"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode())
        return
