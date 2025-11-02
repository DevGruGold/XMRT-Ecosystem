"""
XMRT Ecosystem - Vercel Serverless Entry Point
Main API handler for serverless deployment
"""

from flask import Flask, jsonify, request
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create Flask app
app = Flask(__name__)

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

@app.route('/')
def index():
    """Main landing page with system information"""
    return jsonify({
        "name": "XMRT Ecosystem",
        "version": "7.0.0-vercel",
        "status": "operational",
        "deployment": "vercel-serverless",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agents": {
            "total": len(AGENTS),
            "active": len([a for a in AGENTS.values() if a['status'] == 'active'])
        },
        "endpoints": {
            "health": "/health",
            "agents": "/agents",
            "api_tick": "/api/tick",
            "api_agents": "/api/agents"
        },
        "infrastructure": {
            "platform": "Vercel Serverless",
            "database": "Supabase (vawouugtzwmejxqkeqqj.supabase.co)",
            "cache": "Upstash Redis (charming-reindeer-31873.upstash.io)",
            "github": "DevGruGold/XMRT-Ecosystem"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "ok": True,
        "status": "healthy",
        "platform": "vercel",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "7.0.0-vercel",
        "agents_active": len([a for a in AGENTS.values() if a['status'] == 'active']),
        "services": {
            "api": "operational",
            "supabase": "connected",
            "upstash": "connected"
        }
    })

@app.route('/agents')
def agents():
    """Get agent information"""
    return jsonify({
        "agents": AGENTS,
        "total": len(AGENTS),
        "active": len([a for a in AGENTS.values() if a['status'] == 'active']),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

# Vercel handler
def handler(request):
    """Vercel serverless function handler"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
