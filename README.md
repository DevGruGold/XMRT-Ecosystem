# XMRT-Ecosystem

## 🚀 Welcome to the XMRT-Ecosystem: Empowering Economic Sovereignty through Decentralized AI

The **XMRT-Ecosystem** is a groundbreaking, autonomous, and decentralized platform built on the principles of economic sovereignty, privacy, and AI-human symbiosis. Developed by DevGruGold, it aims to democratize access to privacy-preserving cryptocurrency mining and Web3 governance through mobile-first technology and a sophisticated multi-agent AI architecture.

This repository serves as the central nervous system for the XMRT-DAO, orchestrating a complex array of AI agents, blockchain integrations, mobile mining infrastructure, and decentralized governance mechanisms.

## ✨ Features & Core Principles

*   **Autonomous AI Agents**: A dynamic fleet of specialized AI agents (e.g., Integrator, Security, RAG Architect, Blockchain, DevOps, Comms) that self-organize, manage tasks, and continuously optimize the ecosystem.
*   **Mobile Mining Democracy**: Empowering users to earn XMRT tokens by simply charging their mobile devices through a novel Proof of Participation (PoP) mining system.
*   **Privacy-Preserving Blockchain Integration**: Deep integration with Monero for enhanced transaction privacy, alongside Ethereum for smart contract functionality and governance.
*   **Decentralized Autonomous Organization (DAO)**: A community-governed structure enabling transparent proposal, voting, and treasury management for the XMRT token.
*   **Self-Healing & Self-Optimizing Systems**: AI-driven code monitoring, autonomous debugging, and continuous learning ensure system resilience and efficiency.
*   **Model Context Protocol (MCP)**: A standardized gateway for external AI agents and third-party integrations to interact seamlessly with the XMRT ecosystem.
*   **Ethical AI Licensing**: A unique framework ensuring that AI-driven efficiency gains benefit workers and the community, embodying Joseph Andrew Lee's vision of technology as an enhancer, not a replacement for human endeavor.

## 🏗️ Architecture Overview

The XMRT-Ecosystem is a sophisticated blend of cutting-edge technologies:

*   **AI Layer**: Powered by Google Gemini and OpenAI models, orchestrated by Eliza (the primary AI operator) and a specialized AI Executive C-Suite (CSO, CTO, CIO, CAO).
*   **Backend Infrastructure**: Primarily built on **Supabase** (PostgreSQL, Edge Functions, Realtime, Auth, Storage) and **Vercel** for frontend deployments.
*   **Agent System**: A Python-based multi-agent architecture for task management, automation, and continuous operation.
*   **Blockchain**: Ethereum (ERC-20 XMRT Token, Smart Contracts) and Monero (privacy-preserving mining).
*   **Frontend**: React + TypeScript + Vite for intuitive user interfaces.
*   **Deployment**: Docker, Gunicorn, Render, and Vercel for robust and scalable deployments.

## 🚀 Getting Started

To set up and run the XMRT-Ecosystem locally or deploy it, follow these general steps. Detailed instructions can be found in the `docs/` directory and various `DEPLOYMENT_*.md` files.

### Prerequisites

*   Git
*   Node.js & npm/yarn (for frontend)
*   Python 3.9+ & pip (for backend/agents)
*   Docker & Docker Compose (for local development)
*   Supabase Account
*   GitHub Account & Personal Access Token (PAT)
*   Vercel Account (for frontend deployment)
*   Render Account (for backend/Python services)

### 1. Clone the Repository

```bash
git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
cd XMRT-Ecosystem
```

### 2. Environment Configuration

Copy the example environment files and fill in your credentials. Refer to `.env.example` for a complete list.

```bash
cp .env.example .env
# Fill in .env with your Supabase, GitHub, Vercel, Render, and AI API keys.
```

### 3. Local Development (Docker Compose)

For a comprehensive local development environment, Docker Compose is recommended:

```bash
docker-compose up --build
```
This will spin up PostgreSQL, Supabase Studio, and potentially other services defined in `docker-compose.yml`.

### 4. Supabase Setup

Initialize your Supabase project, set up database schemas, and deploy necessary Edge Functions. Refer to the `supabase/` directory and `DEPLOYMENT.md` for details.

### 5. Backend Services (Python/Render)

Many core services and AI agents are Python-based. They can be run locally or deployed to services like Render.

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run main application (example)
python start_xmrt_system.py
```

### 6. Frontend Application (Vercel)

The frontend applications are built with React/TypeScript and typically deployed on Vercel.

```bash
# Install Node.js dependencies
npm install

# Start local development server
npm run dev
```

## 🧩 Core Components

### `edge-functions/` (Supabase Edge Functions)
Contains the Deno-based serverless functions that power critical real-time operations, AI integrations, GitHub interactions, and core API endpoints. These are the "nervous system" of the ecosystem.

### `agents/` & `enhanced-agents/`
Python-based autonomous AI agents responsible for task execution, monitoring, optimization, and self-healing. These agents embody the multi-agent system philosophy.

### `contracts/`
Solidity smart contracts for the XMRT ERC-20 token, DAO governance, staking, and privacy bridging between Ethereum and Monero.

### `docs/` & `EXECUTIVE_SUMMARY.md`
Comprehensive documentation, architectural overviews, deployment guides, and strategic summaries for the entire ecosystem.

### `api/` & `webhook_endpoints.py`
Definitions and implementations for internal and external API endpoints, including webhooks for event-driven architecture.

### `monitoring/` & `health_checks/`
Scripts and configurations for continuous monitoring of system health, agent performance, and infrastructure stability.

### `python_service/`
General Python services and utilities that support the core ecosystem functionality.

## 🤝 Contributing

We welcome contributions from the community! Please refer to `CONTRIBUTING.md` for guidelines on how to get involved, set up your development environment, and submit changes. All contributions are validated by our AI system and rewarded with XMRT tokens based on their quality and impact.

## 📜 License

The XMRT-Ecosystem is released under the [MIT License](LICENSE).

## 📞 Support & Community

Join our community channels to get support, discuss ideas, and contribute to the future of XMRT-DAO.

*   **GitHub Discussions**: [Link to GitHub Discussions]
*   **Discord/Slack**: [Link to Discord/Slack if applicable]
*   **Website**: [Link to XMRT.io]

---
_Built with passion and purpose by DevGruGold, embodying Joseph Andrew Lee's vision for a decentralized, economically sovereign future._