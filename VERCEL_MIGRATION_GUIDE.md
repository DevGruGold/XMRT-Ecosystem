# 🚀 XMRT-Ecosystem Vercel Migration Guide

## Overview

This guide covers the complete migration of XMRT-Ecosystem from Render to Vercel serverless architecture.

## 🎯 Migration Benefits

### Why Vercel?
- ✅ **Serverless Architecture** - No server management, auto-scaling
- ✅ **Edge Network** - Global CDN for faster response times
- ✅ **Zero Downtime Deployments** - Instant rollbacks
- ✅ **GitHub Integration** - Automatic deployments from commits
- ✅ **Environment Variables** - Secure secret management
- ✅ **Cost Effective** - Pay only for execution time
- ✅ **Developer Experience** - Superior DX with instant previews

### Architecture Changes
- **From:** Flask app on Render (always-on server)
- **To:** Vercel serverless functions (event-driven)

| Component | Render | Vercel |
|-----------|--------|--------|
| Runtime | Continuous | Event-driven |
| Scaling | Manual | Automatic |
| Deployment | Git push + build | Instant (GitHub integration) |
| Cost | Fixed monthly | Usage-based |
| Uptime | 85% (observed) | 99.99% SLA |

## 📁 New File Structure

```
XMRT-Ecosystem/
├── api/                          # Vercel serverless functions
│   ├── index.py                  # Main entry point
│   ├── tick.py                   # Agent coordination endpoint
│   ├── agents.py                 # Agent information API
│   └── __init__.py
├── .github/
│   └── workflows/
│       ├── vercel-deploy.yml                # Vercel deployment
│       ├── agent-coordination-cycle.yml     # 6-hour agent cycles
│       ├── security-guardian-audit.yml      # Daily security audits
│       └── repository-health-check.yml      # 12-hour health checks
├── agent_cycles/                 # Generated coordination reports
├── security_audits/              # Security scan results
├── health_checks/                # Repository health reports
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
└── README.md                     # Updated documentation
```

## 🔧 Step-by-Step Migration

### Step 1: Prepare Repository

```bash
# Clone the repository
git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
cd XMRT-Ecosystem

# Create new branch for migration
git checkout -b vercel-migration

# Copy migration files
cp -r /path/to/migration/files/* .
```

### Step 2: Configure Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Link Project:**
```bash
vercel link
# Follow prompts to create new project or link existing
```

4. **Set Environment Variables:**
```bash
# GitHub Integration
vercel env add GITHUB_TOKEN
vercel env add GITHUB_ORG

# Supabase
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY

# Upstash Redis
vercel env add UPSTASH_REDIS_URL
vercel env add UPSTASH_REDIS_TOKEN

# OpenAI (optional)
vercel env add OPENAI_API_KEY
```

### Step 3: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test serverless functions locally
vercel dev

# Visit http://localhost:3000
# Test endpoints:
# - http://localhost:3000/
# - http://localhost:3000/health
# - http://localhost:3000/agents
# - http://localhost:3000/api/tick
```

### Step 4: Deploy to Vercel

```bash
# Deploy to production
vercel --prod

# Your deployment will be live at:
# https://xmrt-ecosystem.vercel.app (or your custom domain)
```

### Step 5: Configure GitHub Secrets

Go to GitHub repository settings and add these secrets:

```
Repository Settings > Secrets and variables > Actions > New repository secret
```

Required secrets:
- `VERCEL_TOKEN` - Get from https://vercel.com/account/tokens
- `VERCEL_ORG_ID` - Get from Vercel project settings
- `VERCEL_PROJECT_ID` - Get from Vercel project settings
- `VERCEL_DEPLOYMENT_URL` - Your Vercel deployment URL
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/service key
- `UPSTASH_REDIS_URL` - Your Upstash Redis URL
- `UPSTASH_REDIS_TOKEN` - Your Upstash Redis token

### Step 6: Enable GitHub Actions Workflows

```bash
# Commit and push migration files
git add .
git commit -m "🚀 Migrate to Vercel serverless architecture"
git push origin vercel-migration

# Create pull request and merge to main
# GitHub Actions will automatically deploy to Vercel
```

## 🤖 Automated Workflows

### 1. Vercel Deployment (vercel-deploy.yml)
- **Trigger:** Push to main, PR, or manual
- **Purpose:** Automatic deployment to Vercel
- **Duration:** ~2 minutes

### 2. Agent Coordination Cycle (agent-coordination-cycle.yml)
- **Schedule:** Every 6 hours (aligned with xmrtnet)
- **Trigger:** Cron schedule, manual, or code changes
- **Purpose:** Multi-agent consensus and decision making
- **Agents:** Eliza, Security Guardian, DeFi Specialist, Community Manager
- **Output:** `agent_cycles/AGENT_CYCLE_YYYYMMDDHHMM.md`

### 3. Security Guardian Audit (security-guardian-audit.yml)
- **Schedule:** Daily at 2 AM UTC
- **Trigger:** Cron, manual, PR, or code changes
- **Purpose:** Automated security scanning
- **Tools:** Bandit (code), Safety (deps), pip-audit (supply chain)
- **Output:** `security_audits/SECURITY_AUDIT_YYYYMMDD.md`

### 4. Repository Health Check (repository-health-check.yml)
- **Schedule:** Every 12 hours
- **Trigger:** Cron, manual, or push to main
- **Purpose:** Monitor repository health metrics
- **Metrics:** Stars, forks, issues, PRs, commits, contributors
- **Output:** `health_checks/HEALTH_CHECK_YYYYMMDD.md`

## 🔗 Backend Services Integration

### Supabase (Database)
- **URL:** `https://vawouugtzwmejxqkeqqj.supabase.co`
- **Purpose:** Real-time mining state, user data, leaderboards
- **Configuration:** Set `SUPABASE_URL` and `SUPABASE_KEY` in Vercel

### Upstash Redis (Cache & Agent Memory)
- **URL:** `https://charming-reindeer-31873.upstash.io`
- **Purpose:** Agent memory, session management, caching
- **Configuration:** Set `UPSTASH_REDIS_URL` and `UPSTASH_REDIS_TOKEN` in Vercel

### GitHub (Version Control & Automation)
- **Org:** DevGruGold
- **Repo:** XMRT-Ecosystem
- **Purpose:** Code hosting, CI/CD, automated workflows
- **Configuration:** Set `GITHUB_TOKEN` and `GITHUB_ORG` in Vercel

## 📊 Monitoring & Observability

### Vercel Dashboard
- **URL:** https://vercel.com/dashboard
- **Metrics:** Request count, duration, error rate, bandwidth
- **Logs:** Real-time function logs with filtering
- **Deployments:** Full deployment history with instant rollback

### GitHub Actions
- **URL:** https://github.com/DevGruGold/XMRT-Ecosystem/actions
- **Workflows:** View all automated workflow runs
- **Logs:** Detailed execution logs for each step
- **Artifacts:** Download generated reports

### Custom Monitoring
All workflows generate step summaries visible in GitHub Actions UI:
- Agent coordination status
- Security audit results
- Repository health metrics
- Deployment verification

## 🔍 API Endpoints

### Base URL
```
Production: https://xmrt-ecosystem.vercel.app
Local Dev: http://localhost:3000
```

### Available Endpoints

#### GET /
Main landing page with system information
```bash
curl https://xmrt-ecosystem.vercel.app/
```

#### GET /health
Health check endpoint
```bash
curl https://xmrt-ecosystem.vercel.app/health
```

#### GET /agents
Get all agent information
```bash
curl https://xmrt-ecosystem.vercel.app/agents
```

#### GET /api/agents
Get agent details via API
```bash
curl https://xmrt-ecosystem.vercel.app/api/agents
```

#### GET /api/agents/{agent_id}
Get specific agent information
```bash
curl https://xmrt-ecosystem.vercel.app/api/agents/eliza
```

#### POST /api/tick
Trigger agent coordination cycle
```bash
curl -X POST https://xmrt-ecosystem.vercel.app/api/tick \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "cycle_type": "standard"}'
```

## 🚨 Troubleshooting

### Issue: Deployment Fails
**Solution:**
1. Check Vercel build logs in dashboard
2. Verify all environment variables are set
3. Ensure `requirements.txt` has all dependencies
4. Check Python version compatibility (3.11)

### Issue: GitHub Actions Workflow Fails
**Solution:**
1. Check workflow logs for specific error
2. Verify GitHub secrets are configured correctly
3. Ensure proper permissions for GITHUB_TOKEN
4. Check if Vercel deployment URL is accessible

### Issue: Serverless Function Timeout
**Solution:**
1. Default timeout is 60 seconds (configurable in `vercel.json`)
2. Optimize long-running operations
3. Consider breaking into smaller functions
4. Use async operations where possible

### Issue: Environment Variables Not Working
**Solution:**
1. Verify variables are set in Vercel dashboard
2. Check variable names match exactly
3. Redeploy after adding new variables
4. Use `vercel env pull` to test locally

## 📚 Additional Resources

- **Vercel Documentation:** https://vercel.com/docs
- **Vercel Python Runtime:** https://vercel.com/docs/runtimes#official-runtimes/python
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Flask on Vercel:** https://vercel.com/guides/using-flask-with-vercel

## ✅ Migration Checklist

- [ ] Copy migration files to repository
- [ ] Install Vercel CLI
- [ ] Link Vercel project
- [ ] Configure environment variables in Vercel
- [ ] Test locally with `vercel dev`
- [ ] Deploy to Vercel production
- [ ] Configure GitHub secrets
- [ ] Enable GitHub Actions workflows
- [ ] Verify all endpoints work
- [ ] Test agent coordination cycle
- [ ] Monitor first 24 hours of operation
- [ ] Update documentation with new URLs
- [ ] Deprecate Render deployment

## 🎉 Post-Migration

Once migration is complete:
1. ✅ All API endpoints accessible via Vercel URL
2. ✅ GitHub Actions running automated workflows
3. ✅ Agent coordination cycles every 6 hours
4. ✅ Security audits daily
5. ✅ Health checks every 12 hours
6. ✅ Zero downtime deployments
7. ✅ Global edge network performance

## 📞 Support

For issues or questions:
- **GitHub Issues:** https://github.com/DevGruGold/XMRT-Ecosystem/issues
- **GitHub Discussions:** https://github.com/DevGruGold/XMRT-Ecosystem/discussions
- **Vercel Support:** https://vercel.com/support

---

**Migration Status:** Ready for Production  
**Version:** 7.0.0-vercel  
**Last Updated:** 2025-11-02  
**Author:** XMRT Development Team
