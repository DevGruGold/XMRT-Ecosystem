"""
XMRT Ecosystem - Agents API
Serverless endpoint for agent information and status
"""

from flask import Flask, jsonify, request
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

AGENTS = {
    "eliza": {
        "name": "Eliza",
        "role": "Coordinator & Governor",
        "voice": "strategic, synthesizes viewpoints",
        "weight": 1.2,
        "status": "active",
        "capabilities": [
            "Strategic coordination",
            "Multi-agent consensus",
            "Policy governance",
            "Decision synthesis"
        ],
        "last_action": None
    },
    "security_guardian": {
        "name": "Security Guardian",
        "role": "Security & Privacy",
        "voice": "threat-models, privacy-first",
        "weight": 1.1,
        "status": "active",
        "capabilities": [
            "Threat modeling",
            "Vulnerability assessment",
            "Security documentation",
            "Access control"
        ],
        "last_action": None
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "role": "Mining & Tokenomics",
        "voice": "ROI, efficiency, yield",
        "weight": 1.05,
        "status": "active",
        "capabilities": [
            "Mining optimization",
            "Tokenomics analysis",
            "ROI calculation",
            "Yield strategies"
        ],
        "last_action": None
    },
    "community_manager": {
        "name": "Community Manager",
        "role": "Adoption & UX",
        "voice": "onboarding, docs, growth",
        "weight": 1.0,
        "status": "active",
        "capabilities": [
            "Community engagement",
            "Documentation",
            "User onboarding",
            "Feedback management"
        ],
        "last_action": None
    }
}

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agent information"""
    return jsonify({
        "agents": AGENTS,
        "total": len(AGENTS),
        "active": len([a for a in AGENTS.values() if a['status'] == 'active']),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent information"""
    if agent_id not in AGENTS:
        return jsonify({
            "error": "Agent not found",
            "available_agents": list(AGENTS.keys())
        }), 404
    
    return jsonify({
        "agent": AGENTS[agent_id],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
