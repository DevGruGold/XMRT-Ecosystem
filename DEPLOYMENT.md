# XMRTNET Deployment Guide

## Overview

This guide provides instructions for deploying and running the XMRTNET DAO prototype with Eliza AI integration.

## Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+ and pip
- Git
- Sepolia testnet ETH for AI agent wallets
- OpenAI API key for Eliza functionality

## Environment Setup

### 1. Backend Configuration

Create a `.env` file in `backend/xmrt-dao-backend/`:

```env
# Blockchain Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
XMRT_CONTRACT_ADDRESS=0x77307DFbc436224d5e6f2048d2b6bDfA66998a15
CHAIN_ID=11155111

# AI Agent Wallets (Generate new keys for production)
GOVERNANCE_AGENT_PRIVATE_KEY=your_governance_agent_private_key
TREASURY_AGENT_PRIVATE_KEY=your_treasury_agent_private_key
COMMUNITY_AGENT_PRIVATE_KEY=your_community_agent_private_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### 2. Install Dependencies

Backend:
```bash
cd backend/xmrt-dao-backend
source venv/bin/activate
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend/xmrt-dao-frontend
pnpm install
```

## Running the Application

### 1. Start Backend Server

```bash
cd backend/xmrt-dao-backend
source venv/bin/activate
python src/main.py
```

The backend will run on `http://localhost:5000`

### 2. Start Frontend Development Server

```bash
cd frontend/xmrt-dao-frontend
pnpm run dev --host
```

The frontend will run on `http://localhost:5173`

## API Endpoints

### Blockchain Endpoints
- `GET /api/blockchain/contract-info` - Get contract information
- `GET /api/blockchain/balance/{address}` - Get XMRT balance
- `GET /api/blockchain/stake-info/{address}` - Get staking information
- `GET /api/blockchain/network-status` - Get network status

### Eliza AI Endpoints
- `POST /api/eliza/chat` - Chat with Eliza
- `POST /api/eliza/analyze-proposal` - Analyze governance proposals
- `POST /api/eliza/treasury-recommendation` - Get treasury recommendations
- `GET /api/eliza/status` - Get Eliza status

### AI Agents Endpoints
- `GET /api/ai-agents/agents` - List all AI agents
- `GET /api/ai-agents/agent/{type}` - Get specific agent info
- `POST /api/ai-agents/agent/{type}/generate-wallet` - Generate new wallet
- `GET /api/ai-agents/funding-instructions` - Get funding instructions

## AI Agent Wallet Setup

1. Generate new wallets for each agent using the API:
   ```bash
   curl -X POST http://localhost:5000/api/ai-agents/agent/governance/generate-wallet
   curl -X POST http://localhost:5000/api/ai-agents/agent/treasury/generate-wallet
   curl -X POST http://localhost:5000/api/ai-agents/agent/community/generate-wallet
   ```

2. Fund the wallets with Sepolia ETH using faucets:
   - https://faucets.chain.link/sepolia
   - https://sepolia-faucet.pk910.de/
   - https://www.alchemy.com/faucets/ethereum-sepolia

3. Update the `.env` file with the generated private keys

## Smart Contract Integration

The system integrates with the XMRT token contract deployed at:
`0x77307DFbc436224d5e6f2048d2b6bDfA66998a15` (Sepolia Testnet)

Key features:
- ERC20 token with 21M total supply
- Staking mechanism with 7-day minimum period
- 10% early unstaking penalty
- Role-based access control for AI agents

## Security Notes

⚠️ **Important Security Considerations:**

1. This is a testnet prototype - do not use with real funds
2. Generate new private keys for production deployment
3. Use environment variables for all sensitive data
4. The smart contract has not been audited
5. AI agent wallets should use hardware security modules in production

## Troubleshooting

### Common Issues

1. **Backend fails to start**: Check that all dependencies are installed and the virtual environment is activated
2. **Frontend build errors**: Ensure Node.js 18+ and pnpm are installed
3. **Blockchain connection issues**: Verify Infura project ID and RPC URL
4. **Eliza not responding**: Check OpenAI API key configuration

### Logs

Backend logs are output to the console. For production deployment, configure proper logging.

## Production Deployment

For production deployment:

1. Use a proper database (PostgreSQL/MongoDB) instead of SQLite
2. Set up proper environment variable management
3. Configure HTTPS and security headers
4. Use a process manager like PM2 for the backend
5. Build and serve the frontend through a CDN
6. Implement proper monitoring and alerting
7. Conduct security audits of smart contracts
8. Use hardware security modules for AI agent wallets

## Support

For issues and questions:
- GitHub Issues: https://github.com/DevGruGold/XMRTNET/issues
- Discord: https://discord.gg/xmrtdao
- Twitter: @xmrtdao

