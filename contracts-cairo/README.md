# XMRT Ecosystem Cairo Contracts

This directory contains the Cairo smart contracts for the XMRT ecosystem on Starknet.

## Contracts Overview

### Core Contracts

1. **XMRT Token (`xmrt.cairo`)**
   - ERC-20 compatible token with staking functionality
   - Maximum supply of 21,000,000 tokens
   - Built-in staking with minimum lock period
   - Penalty mechanism for early unstaking

2. **Governance (`governance.cairo`)**
   - Comprehensive DAO governance system
   - Proposal creation and voting mechanisms
   - Quorum and threshold requirements
   - Time-based voting periods

3. **Treasury (`treasury.cairo`)**
   - DAO treasury management
   - Fund allocation and execution
   - Emergency pause functionality
   - Multi-token support

4. **Staking Rewards (`staking_rewards.cairo`)**
   - Advanced staking rewards system
   - Tier-based multipliers
   - Lock period incentives
   - Automatic reward calculation

5. **Cross-Chain Bridge (`cross_chain_bridge.cairo`)**
   - Multi-chain token bridging
   - Validator consensus mechanism
   - Daily limits and security features
   - Transaction confirmation system

6. **Oracle Manager (`oracle_manager.cairo`)**
   - Price feed management
   - Multi-oracle data aggregation
   - Historical price tracking
   - Emergency price mechanisms

### Utility Contracts

7. **Agent Manager (`agent_manager.cairo`)**
   - Role-based access control
   - Agent registration and management
   - Permission system

8. **Autonomous DAO (`autonomous_dao.cairo`)**
   - Core DAO functionality
   - Proposal management
   - Basic governance operations

9. **Autonomous DAO Core (`autonomous_dao_core.cairo`)**
   - Extended DAO functionality
   - Parameter management
   - Governance contract integration

10. **AI Agent Interface (`ai_agent_interface.cairo`)**
    - Interface for AI agent interactions
    - Standardized agent communication

11. **Autonomous Agent Registry (`autonomous_agent_registry.cairo`)**
    - Agent registration system
    - Agent discovery and management

## Testing

The `test_suite.cairo` file contains comprehensive tests for all contracts including:

- Unit tests for individual contract functions
- Integration tests for cross-contract interactions
- Security scenario testing
- Performance benchmarks
- Mock contracts for testing

## Building and Deployment

### Prerequisites

- Starknet development environment
- Scarb (Cairo package manager)
- snforge (for testing)

### Build Commands

```bash
# Build all contracts
scarb build

# Run tests
scarb test

# Format code
scarb fmt
```

### Deployment

1. Compile contracts using Scarb
2. Deploy to Starknet testnet/mainnet
3. Initialize contracts with proper parameters
4. Set up inter-contract connections

## Contract Architecture

```
XMRT Token
    ├── Staking Rewards
    ├── Governance
    │   └── Treasury
    ├── Cross-Chain Bridge
    └── Oracle Manager

Agent Manager
    ├── Autonomous DAO
    ├── Autonomous DAO Core
    └── Autonomous Agent Registry
```

## Security Features

- Access control mechanisms
- Emergency pause functionality
- Reentrancy protection
- Overflow/underflow protection
- Multi-signature requirements
- Time-based restrictions

## Gas Optimization

- Efficient storage patterns
- Minimal external calls
- Optimized loops and calculations
- Batch operations where possible

## Upgrade Strategy

- Proxy pattern implementation
- Governance-controlled upgrades
- Migration mechanisms
- Backward compatibility

## Contributing

1. Follow Cairo coding standards
2. Add comprehensive tests for new features
3. Update documentation
4. Ensure security best practices

## License

This project is licensed under the MIT License.

