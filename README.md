# 🚀 XMRT Ecosystem

<div align="center">

![XMRT Ecosystem](https://img.shields.io/badge/XMRT-Ecosystem-blue?style=for-the-badge)
[![Stars](https://img.shields.io/github/stars/DevGruGold/XMRT-Ecosystem?style=flat-square)](https://github.com/DevGruGold/XMRT-Ecosystem/stargazers)
[![Forks](https://img.shields.io/github/forks/DevGruGold/XMRT-Ecosystem?style=flat-square)](https://github.com/DevGruGold/XMRT-Ecosystem/network/members)
[![Issues](https://img.shields.io/github/issues/DevGruGold/XMRT-Ecosystem?style=flat-square)](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
[![License](https://img.shields.io/github/license/DevGruGold/XMRT-Ecosystem?style=flat-square)](./LICENSE)

**Full-stack decentralized autonomous organization (DAO) with AI-powered agents and blockchain integration**

[Features](#-features) • [Getting Started](#-getting-started) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 About

**XMRT Ecosystem** is a comprehensive DAO platform that combines AI-driven automation, multi-agent coordination, and blockchain technology to create a self-governing, intelligent ecosystem. Built with ElizaOS for autonomous operations and Ethereum smart contracts for decentralized governance.

### 🎯 Key Highlights

- 🤖 **AI-Powered Agents**: 93+ scheduled automations handling community engagement, analytics, security, and governance
- 🔄 **Multi-Agent Coordination**: Sophisticated agent orchestration with memory, learning, and task management
- ⚡ **Real-time Analytics**: Comprehensive monitoring and reporting systems
- 🔐 **Blockchain Integration**: Smart contracts deployed on Ethereum Sepolia testnet
- 🌐 **Full-Stack Platform**: Modern web dashboard with Next.js + React + Supabase
- 🛡️ **Security First**: Automated security scans, code analysis, and threat detection

---

## ✨ Features

### 🧠 **ElizaOS Integration**
- Autonomous reward tracking and distribution
- Context-aware decision making
- Self-learning and adaptive behavior
- Character-based AI personalities

### 🤝 **Community Automation**
- **GitHub Triage**: Automatic issue labeling and prioritization
- **PR Review**: AI-powered code review and feedback
- **Discussion Management**: Automated community engagement
- **Security Scanning**: Malicious content detection and removal

### 📊 **Analytics & Monitoring**
- Real-time metrics collection and visualization
- GitHub activity tracking and insights
- System health monitoring
- Performance analytics dashboard

### 🏛️ **DAO Governance**
- Proposal creation and voting system
- Token-based governance mechanisms
- Transparent decision-making process
- Smart contract integration

### 🔧 **Edge Functions**
- 143 deployed Supabase Edge Functions
- Task orchestration and automation
- System status monitoring
- API integrations

### 🎨 **Unified Dashboard**
- Reward claims interface
- Wallet integration (CashDapp)
- Analytics visualization
- Agent activity monitoring

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18
- **Styling**: TailwindCSS
- **State Management**: React Hooks + Context API

### Backend
- **Runtime**: Node.js 20+, Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **Edge Functions**: Supabase Functions
- **APIs**: REST + GraphQL

### AI & Automation
- **AI Engine**: ElizaOS
- **LLM Integration**: OpenAI GPT-4
- **Agent Framework**: Custom multi-agent system
- **Scheduling**: Cron-based automation (93 scheduled functions)

### Blockchain
- **Network**: Ethereum Sepolia Testnet
- **Smart Contracts**: 
  - XMRT Token: `0x77307DFbc436224d5e6f2048d2b6bDfA66998a15`
  - IP-NFT: `0x9de91fc136a846d7442d1321a2d1b6aaef494eda`
- **Framework**: Hardhat

### DevOps & Infrastructure
- **CI/CD**: GitHub Actions (26 workflows)
- **Containerization**: Docker + Docker Compose
- **Deployment**: Vercel (frontend), Supabase (backend)
- **Monitoring**: Custom health checks + logging

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+ and npm/pnpm
- **Python** 3.11+
- **Docker** (optional, for containerized development)
- **Git**
- **Supabase CLI** (for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
   cd XMRT-Ecosystem
   ```

2. **Install dependencies**
   ```bash
   # Node.js dependencies
   npm install

   # Python dependencies
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Copy example environment files
   cp .env.example .env
   cp .env.auth.example .env.auth

   # Edit .env with your configuration
   # Required variables:
   # - SUPABASE_URL
   # - SUPABASE_KEY
   # - GITHUB_TOKEN
   # - OPENAI_API_KEY
   ```

4. **Database Setup**
   ```bash
   # Initialize Supabase locally (optional)
   supabase init
   supabase start

   # Run migrations
   supabase db push
   ```

5. **Run Development Server**
   ```bash
   # Start frontend
   npm run dev

   # Start backend (in another terminal)
   python enhanced_main.py
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Supabase Studio: http://localhost:54323
   - API: http://localhost:5000

### Quick Start with Docker

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📁 Project Structure

```
XMRT-Ecosystem/
├── .github/
│   └── workflows/          # GitHub Actions (26 automated workflows)
├── agents/                 # AI agent definitions and configurations
├── api/                    # API endpoints and routes
├── app/                    # Next.js application (frontend)
├── supabase/
│   ├── functions/          # Edge Functions (143 deployed)
│   └── migrations/         # Database migrations
├── contracts/              # Smart contracts (Solidity)
├── scripts/                # Utility and deployment scripts
├── monitoring/             # Health checks and logging
├── docs/                   # Additional documentation
├── config/                 # Configuration files
├── enhanced_main.py        # Main backend application
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Key Files

- **`enhanced_main.py`**: Main backend server with multi-agent coordination
- **`enhanced_autonomous_controller.py`**: Agent orchestration and task management
- **`analytics_system.py`**: Real-time metrics collection and analysis
- **`github_manager.py`**: GitHub API integration and automation
- **`agents_config.py`**: Agent personalities and behaviors

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Dashboard   │  │    Wallet    │  │   Analytics     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                        │ REST/GraphQL API
┌────────────────────────┴────────────────────────────────────┐
│                   Backend (Python/Node.js)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Multi-Agent Coordinator (ElizaOS)            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │  │
│  │  │Analytics │  │Community │  │  Governance Agent │  │  │
│  │  │  Agent   │  │  Agent   │  │                   │  │  │
│  │  └──────────┘  └──────────┘  └───────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────┴──────┐ ┌──────┴──────┐ ┌─────┴──────┐
│   Supabase   │ │   GitHub    │ │ Blockchain │
│  (Database)  │ │     API     │ │  (Sepolia) │
└──────────────┘ └─────────────┘ └────────────┘
```

### Agent Workflow

1. **Scheduler** triggers scheduled functions
2. **Coordinator** dispatches tasks to appropriate agents
3. **Agents** execute tasks with context and memory
4. **Learning System** analyzes outcomes and improves
5. **Analytics** collects metrics and generates insights
6. **Frontend** displays results in real-time

---

## 📚 Documentation

- **[Deployment Guide](./DEPLOYMENT.md)**: Production deployment instructions
- **[Development Guide](./DEVELOPMENT.md)**: Local development setup
- **[Contributing Guidelines](./CONTRIBUTING.md)**: How to contribute
- **[Changelog](./CHANGELOG.md)**: Version history and updates
- **[API Documentation](./docs/api/)**: API endpoints and usage

### Additional Resources

- 📊 **[Supabase Dashboard](https://supabase.com/dashboard/project/vawouugtzwmejxqkeqqj)**: View functions and logs
- 🔐 **[GitHub Actions](https://github.com/DevGruGold/XMRT-Ecosystem/actions)**: CI/CD workflows
- 💬 **[Discussions](https://github.com/DevGruGold/XMRT-Ecosystem/discussions)**: Community discussions
- 📈 **[Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)**: Bug reports and features

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
npm test

# Run Python tests
pytest

# Run specific test suite
npm test -- agents
```

### Code Quality

```bash
# Lint code
npm run lint
pylint **/*.py

# Format code
npm run format
black .

# Type checking
npm run type-check
mypy .
```

### Building for Production

```bash
# Build frontend
npm run build

# Build Docker image
docker build -t xmrt-ecosystem .
```

---

## 🚢 Deployment

### Supabase Edge Functions

```bash
# Deploy all functions
supabase functions deploy

# Deploy specific function
supabase functions deploy function-name
```

### Vercel (Frontend)

```bash
# Deploy to production
vercel --prod

# Or push to main branch for automatic deployment
```

### Smart Contracts

```bash
# Deploy to testnet
cd contracts
npx hardhat run scripts/deploy.js --network sepolia
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure CI passes

---

## 📊 Project Stats

- **Total Functions**: 143 deployed edge functions
- **Scheduled Automations**: 93 active scheduled functions
- **GitHub Workflows**: 26 automated workflows
- **Smart Contracts**: 2 deployed on Sepolia
- **Agent Personalities**: Multiple AI characters
- **Automation Coverage**: 65% of operations automated

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](./LICENSE) file for details.

---

## 📞 Contact & Community

- **GitHub**: [@DevGruGold](https://github.com/DevGruGold)
- **Issues**: [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DevGruGold/XMRT-Ecosystem/discussions)

---

## 🙏 Acknowledgments

- **ElizaOS**: AI agent framework
- **Supabase**: Backend infrastructure
- **OpenAI**: LLM capabilities
- **Ethereum**: Blockchain infrastructure
- **Community Contributors**: Thank you!

---

<div align="center">

**Made with ❤️ by the XMRT Community**

[⬆ Back to Top](#-xmrt-ecosystem)

</div>
