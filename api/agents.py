"""
XMRT Ecosystem - Agents API
Vercel Serverless Function
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from api.supabase_client import get_registered_agents, register_agent, log_activity

# Agent information
AGENTS = {
    "eliza": {
        "name": "Eliza",
        "role": "Coordinator & Governor",
        "voice": "strategic, synthesizes viewpoints",
        "weight": 1.2,
        "status": "active"
    },
    "security_guardian": {
        "name": "Security Guardian",
        "role": "Security & Privacy",
        "voice": "threat-models, privacy-first",
        "weight": 1.1,
        "status": "active"
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "role": "Mining & Tokenomics",
        "voice": "ROI, efficiency, yield",
        "weight": 1.05,
        "status": "active"
    },
    "community_manager": {
        "name": "Community Manager",
        "role": "Adoption & UX",
        "voice": "onboarding, docs, growth",
        "weight": 1.0,
        "status": "active"
    }
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request for agents"""
        
        # Parse URL to check for agent_id
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Check if specific agent requested
        agent_id = query_params.get('agent_id', [None])[0]
        
        if agent_id:
            # Return specific agent
            if agent_id in AGENTS:
                response_data = {
                    "agent_id": agent_id,
                    "agent": AGENTS[agent_id],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                status_code = 200
            else:
                response_data = {
                    "error": "Agent not found",
                    "agent_id": agent_id,
                    "available_agents": list(AGENTS.keys())
                }
                status_code = 404
        else:
            # Return all agents
            response_data = {
                "agents": AGENTS,
                "count": len(AGENTS),
                "active": len([a for a in AGENTS.values() if a['status'] == 'active']),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            status_code = 200
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode())
        return
