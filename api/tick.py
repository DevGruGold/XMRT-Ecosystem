"""
XMRT Ecosystem - Agent Coordination Trigger API
Vercel Serverless Function
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from .supabase_client import log_activity, register_agent

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to trigger agent coordination"""
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
            trigger = data.get('trigger', 'unknown')
        except:
            trigger = 'unknown'
        
        response_data = {
            "ok": True,
            "message": "Agent coordination cycle triggered",
            "trigger": trigger,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "note": "Coordination will be executed by GitHub Actions workflow"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode())
        return
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
