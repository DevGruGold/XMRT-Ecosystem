# XMRT Autonomous Eliza Deployment Guide

## Render Deployment Settings:

### Web Service Configuration:
- **Name:** xmrt-autonomous-eliza
- **Environment:** Node
- **Build Command:** `pnpm install && pnpm build`
- **Start Command:** `pnpm start`
- **Node Version:** 22.12.0

### Required Environment Variables:
```
NODE_ENV=production
NODE_VERSION=22.12.0
PORT=10000
DATABASE_URL=postgresql://[your-render-postgres-url]
```

### Database Setup:
1. Create PostgreSQL database on Render
2. Add PG Vector extension for Eliza's memory system
3. Update DATABASE_URL environment variable

### Pre-deployment Checklist:
- [ ] All API keys added to environment variables
- [ ] Database connection string configured
- [ ] Social media tokens added
- [ ] Blockchain RPC URLs configured

### Post-deployment:
- Your Autonomous Eliza will be available at: https://xmrt-autonomous-eliza.onrender.com
- She will have persistent memory via PostgreSQL
- 24/7 operation for DAO management
- Multi-chain support enabled

## Troubleshooting:
- If build fails, check Node.js version is set to 22.12.0
- Ensure all environment variables are properly configured
- Check logs for missing dependencies or API key issues
