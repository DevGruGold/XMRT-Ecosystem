# 🤖 XMRT-Ecosystem - Vercel Serverless Edition

**Version:** 7.0.0-vercel  
**Platform:** Vercel Serverless Functions  
**Status:** 🟢 Operational  
**Deployment:** Automatic via GitHub Actions

---

## 🎯 Overview

XMRT-Ecosystem is a production-ready, AI-governed decentralized autonomous organization (DAO) now powered by **Vercel serverless architecture**. This migration brings automatic scaling, global edge performance, and zero-downtime deployments.

### Key Features

- **🤖 Four Autonomous AI Agents:** Eliza (Coordinator), Security Guardian, DeFi Specialist, Community Manager
- **⚡ Serverless Architecture:** Event-driven, auto-scaling, pay-per-use
- **🌐 Global Edge Network:** Fast response times worldwide
- **🔄 Automated Workflows:** 6-hour coordination cycles, daily security audits, 12-hour health checks
- **🔒 Secure by Design:** Automated security scanning and dependency audits
- **📊 Real-time Monitoring:** Comprehensive observability and reporting

---

## 🏗️ Architecture

### Technology Stack

**Frontend Deployment:**
- Multiple Vercel deployments (User ID: `uYPuVgepZnTkCfV20TmJ28Dq`)
- React, TypeScript, Next.js

**Backend Services:**
- **Platform:** Vercel Serverless Functions (Python 3.11)
- **Database:** Supabase (`vawouugtzwmejxqkeqqj.supabase.co`)
- **Cache/Memory:** Upstash Redis (`charming-reindeer-31873.upstash.io`)
- **Version Control:** GitHub (DevGruGold/XMRT-Ecosystem)

**CI/CD:**
- GitHub Actions for automated workflows
- Vercel for instant deployments

### Multi-Agent System

| Agent | Role | Weight | Status |
|-------|------|--------|--------|
| 🎯 **Eliza** | Coordinator & Governor | 1.2 | ✅ Active |
| 🔒 **Security Guardian** | Security & Privacy | 1.1 | ✅ Active |
| 💰 **DeFi Specialist** | Mining & Tokenomics | 1.05 | ✅ Active |
| 👥 **Community Manager** | Adoption & UX | 1.0 | ✅ Active |

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (for Vercel CLI)
- Python 3.11+
- Git
- Vercel account

### Local Development

```bash
# Clone repository
git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
cd XMRT-Ecosystem

# Install Vercel CLI
npm install -g vercel

# Install Python dependencies
pip install -r requirements.txt

# Login to Vercel
vercel login

# Link project
vercel link

# Pull environment variables
vercel env pull .env.local

# Run development server
vercel dev

# Visit http://localhost:3000
```

### Deployment

```bash
# Deploy to production
vercel --prod

# Or push to main branch for automatic deployment
git push origin main
```

---

## 📡 API Endpoints

### Base URL
```
Production: https://xmrt-ecosystem.vercel.app
```

### Endpoints

#### System Information
```http
GET /
```
Returns system status, agent information, and infrastructure details.

#### Health Check
```http
GET /health
```
Returns platform health, service status, and agent activity.

#### Agent Information
```http
GET /agents
GET /api/agents
GET /api/agents/{agent_id}
```
Returns agent details, capabilities, and current status.

#### Agent Coordination
```http
POST /api/tick
Content-Type: application/json

{
  "trigger": "manual|github_actions",
  "cycle_type": "standard|emergency|analysis"
}
```
Triggers a coordination cycle across all agents.

### Example Requests

```bash
# Health check
curl https://xmrt-ecosystem.vercel.app/health

# Get all agents
curl https://xmrt-ecosystem.vercel.app/agents

# Get specific agent
curl https://xmrt-ecosystem.vercel.app/api/agents/eliza

# Trigger coordination cycle
curl -X POST https://xmrt-ecosystem.vercel.app/api/tick \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "cycle_type": "standard"}'
```

---

## 🔄 Automated Workflows

### 1. 🚀 Vercel Deployment
- **Trigger:** Push to main, PR, manual
- **Frequency:** On-demand
- **Purpose:** Automatic deployment to Vercel
- **File:** `.github/workflows/vercel-deploy.yml`

### 2. 🤖 Agent Coordination Cycle
- **Trigger:** Every 6 hours, manual, code changes
- **Frequency:** Every 6 hours (aligned with xmrtnet)
- **Purpose:** Multi-agent consensus building
- **Output:** `agent_cycles/AGENT_CYCLE_*.md`
- **File:** `.github/workflows/agent-coordination-cycle.yml`

### 3. 🔒 Security Guardian Audit
- **Trigger:** Daily at 2 AM UTC, manual, PR
- **Frequency:** Daily
- **Purpose:** Automated security scanning
- **Tools:** Bandit, Safety, pip-audit
- **Output:** `security_audits/SECURITY_AUDIT_*.md`
- **File:** `.github/workflows/security-guardian-audit.yml`

### 4. 🏥 Repository Health Check
- **Trigger:** Every 12 hours, manual, push
- **Frequency:** Every 12 hours
- **Purpose:** Monitor repository metrics
- **Output:** `health_checks/HEALTH_CHECK_*.md`
- **File:** `.github/workflows/repository-health-check.yml`

---

## 🔧 Configuration

### Environment Variables

Configure in Vercel dashboard or via CLI:

```bash
# Required
GITHUB_TOKEN          # GitHub API access
GITHUB_ORG            # GitHub organization (DevGruGold)
SUPABASE_URL          # Supabase project URL
SUPABASE_KEY          # Supabase anon/service key
UPSTASH_REDIS_URL     # Upstash Redis REST URL
UPSTASH_REDIS_TOKEN   # Upstash Redis token

# Optional
OPENAI_API_KEY        # For AI-powered rationale generation
LOG_LEVEL             # Logging level (INFO, DEBUG, WARNING)
```

### GitHub Secrets

Configure in repository settings:

```
Settings > Secrets and variables > Actions
```

Required secrets:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `VERCEL_DEPLOYMENT_URL`
- All backend service credentials

---

## 📊 Monitoring

### Vercel Dashboard
- Real-time function logs
- Performance metrics
- Deployment history
- Usage analytics

### GitHub Actions
- Workflow execution logs
- Step summaries with detailed reports
- Artifact downloads (reports, audits)

### Custom Reports

Generated automatically by workflows:
- **Agent Cycles:** Coordination decisions and consensus
- **Security Audits:** Vulnerability scans and recommendations
- **Health Checks:** Repository metrics and health scores

---

## 🗂️ Project Structure

```
XMRT-Ecosystem/
├── api/                          # Vercel serverless functions
│   ├── index.py                  # Main entry point
│   ├── tick.py                   # Agent coordination
│   └── agents.py                 # Agent information
├── .github/
│   └── workflows/                # GitHub Actions
│       ├── vercel-deploy.yml
│       ├── agent-coordination-cycle.yml
│       ├── security-guardian-audit.yml
│       └── repository-health-check.yml
├── agent_cycles/                 # Coordination reports
├── security_audits/              # Security scan results
├── health_checks/                # Health reports
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
├── VERCEL_MIGRATION_GUIDE.md    # Migration documentation
└── README.md                     # This file
```

---

## 🔍 Development

### Testing Locally

```bash
# Start Vercel dev server
vercel dev

# Test endpoints
curl http://localhost:3000/health
curl http://localhost:3000/agents
curl -X POST http://localhost:3000/api/tick
```

### Adding New Serverless Functions

1. Create new file in `api/` directory:
```python
# api/your_function.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/your_function')
def your_function():
    return jsonify({"status": "success"})

def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
```

2. Test locally:
```bash
vercel dev
curl http://localhost:3000/api/your_function
```

3. Deploy:
```bash
vercel --prod
```

---

## 📚 Documentation

- **[Migration Guide](VERCEL_MIGRATION_GUIDE.md)** - Complete migration documentation
- **[GitHub Repository](https://github.com/DevGruGold/XMRT-Ecosystem)** - Source code
- **[GitHub Actions](https://github.com/DevGruGold/XMRT-Ecosystem/actions)** - Workflow runs
- **[Vercel Documentation](https://vercel.com/docs)** - Platform docs
- **[xmrtnet Reference](https://github.com/DevGruGold/xmrtnet)** - Similar implementation

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Areas

- 🤖 Agent capabilities and coordination logic
- 🔒 Security enhancements and auditing
- 📊 Analytics and monitoring improvements
- 📝 Documentation updates
- 🐛 Bug fixes and optimizations

---

## 🔗 Related Projects

- **[xmrtnet](https://github.com/DevGruGold/xmrtnet)** - Reference implementation with autonomous analytics
- **[MESHNET](https://github.com/DevGruGold/MESHNET)** - Offline mesh networking
- **[MobileMonero](https://mobilemonero.com)** - Mobile mining hub

---

## 📄 License

This project is licensed under the Apache License 2.0. See individual files for details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- **Discussions:** [GitHub Discussions](https://github.com/DevGruGold/XMRT-Ecosystem/discussions)
- **Email:** eliza@xmrt-ecosystem.io

---

## 🎉 Current Status

✅ **Migration Complete**  
✅ **All Systems Operational**  
✅ **Automated Workflows Active**  
✅ **Agent Coordination Running**  
✅ **Security Audits Scheduled**  
✅ **Health Monitoring Enabled**

**Deployment:** https://xmrt-ecosystem.vercel.app  
**Version:** 7.0.0-vercel  
**Platform:** Vercel Serverless  
**Uptime Target:** 99.99%  

---

**Built with ❤️ by the XMRT Team**  
*Humans and AI Working Together*

**Last Updated:** 2025-11-02  
**Status:** 🟢 Production Ready
