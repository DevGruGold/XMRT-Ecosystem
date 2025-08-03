"""
Blockchain Utilities for XMRT DAO
Handles all blockchain interactions and smart contract operations
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from web3 import Web3
from eth_account import Account
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class BlockchainUtils:
    """Utility class for blockchain operations"""

    def __init__(self):
        # Initialize Web3 connections
        self.networks = {
            "sepolia": {
                "rpc_url": os.getenv(
                    "SEPOLIA_RPC_URL",
                    "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID",
                ),
                "chain_id": 11155111,
            },
            "ethereum": {
                "rpc_url": os.getenv(
                    "ETHEREUM_RPC_URL",
                    "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
                ),
                "chain_id": 1,
            },
            "polygon": {
                "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
                "chain_id": 137,
            },
            "bsc": {
                "rpc_url": os.getenv(
                    "BSC_RPC_URL", "https://bsc-dataseed1.binance.org"
                ),
                "chain_id": 56,
            },
            "avalanche": {
                "rpc_url": os.getenv(
                    "AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc"
                ),
                "chain_id": 43114,
            },
            "arbitrum": {
                "rpc_url": os.getenv(
                    "ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"
                ),
                "chain_id": 42161,
            },
            "optimism": {
                "rpc_url": os.getenv("OPTIMISM_RPC_URL", "https://mainnet.optimism.io"),
                "chain_id": 10,
            },
        }

        # Initialize primary network (Sepolia for testing)
        self.primary_network = "sepolia"
        self.w3 = Web3(
            Web3.HTTPProvider(self.networks[self.primary_network]["rpc_url"])
        )

        # Contract addresses
        self.contract_addresses = {
            "xmrt": os.getenv(
                "XMRT_CONTRACT_ADDRESS", "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
            ),
            "dao_governance": os.getenv("DAO_GOVERNANCE_ADDRESS"),
            "dao_treasury": os.getenv("DAO_TREASURY_ADDRESS"),
            "ai_agent_interface": os.getenv("AI_AGENT_INTERFACE_ADDRESS"),
            "cross_chain": os.getenv("XMRT_CROSS_CHAIN_ADDRESS"),
            "layer_zero_oft": os.getenv("XMRT_OFT_ADDRESS"),
        }

        # Load contract ABIs
        self.contract_abis = self.load_contract_abis()

        # Initialize contracts
        self.contracts = self.initialize_contracts()

        logger.info("Blockchain utilities initialized")

    def load_contract_abis(self) -> Dict[str, Any]:
        """Load contract ABIs"""
        try:
            # In production, load from files or environment
            # For now, return minimal ABIs
            return {
                "xmrt": [
                    {
                        "inputs": [{"name": "amount", "type": "uint256"}],
                        "name": "stake",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function",
                    },
                    {
                        "inputs": [],
                        "name": "totalSupply",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function",
                    },
                ],
                "dao_governance": [
                    {
                        "inputs": [
                            {"name": "proposalId", "type": "uint256"},
                            {"name": "support", "type": "bool"},
                        ],
                        "name": "castVote",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function",
                    },
                    {
                        "inputs": [],
                        "name": "getActiveProposals",
                        "outputs": [{"name": "", "type": "uint256[]"}],
                        "stateMutability": "view",
                        "type": "function",
                    },
                ],
                "dao_treasury": [
                    {
                        "inputs": [],
                        "name": "getTreasuryBalance",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function",
                    }
                ],
            }
        except Exception as e:
            logger.error(f"Error loading contract ABIs: {e}")
            return {}

    def initialize_contracts(self) -> Dict[str, Any]:
        """Initialize contract instances"""
        contracts = {}

        try:
            for name, address in self.contract_addresses.items():
                if address and name in self.contract_abis:
                    contracts[name] = self.w3.eth.contract(
                        address=Web3.to_checksum_address(address),
                        abi=self.contract_abis[name],
                    )

            logger.info(f"Initialized {len(contracts)} contracts")
            return contracts

        except Exception as e:
            logger.error(f"Error initializing contracts: {e}")
            return {}

    async def get_active_proposals(self) -> List[Dict[str, Any]]:
        """Get active governance proposals"""
        try:
            if "dao_governance" not in self.contracts:
                return []

            # Get proposal IDs
            proposal_ids = (
                self.contracts["dao_governance"].functions.getActiveProposals().call()
            )

            proposals = []
            for proposal_id in proposal_ids:
                # Get proposal details (mock implementation)
                proposal = {
                    "id": proposal_id,
                    "description": f"Proposal {proposal_id}",
                    "target": "0x0000000000000000000000000000000000000000",
                    "value": 0,
                    "calldata": "0x",
                    "start_time": datetime.now().timestamp(),
                    "end_time": datetime.now().timestamp() + 604800,  # 7 days
                    "votes_for": 0,
                    "votes_against": 0,
                    "emergency": False,
                }
                proposals.append(proposal)

            return proposals

        except Exception as e:
            logger.error(f"Error getting active proposals: {e}")
            return []

    async def cast_vote(self, proposal_id: int, support: bool) -> str:
        """Cast a vote on a proposal"""
        try:
            if "dao_governance" not in self.contracts:
                raise ValueError("Governance contract not available")

            # Get agent account
            agent_key = os.getenv("GOVERNANCE_AGENT_PRIVATE_KEY")
            if not agent_key:
                raise ValueError("Agent private key not configured")

            account = Account.from_key(agent_key)

            # Build transaction
            function = self.contracts["dao_governance"].functions.castVote(
                proposal_id, support
            )

            # Get gas estimate
            gas_estimate = function.estimateGas({"from": account.address})

            # Build transaction
            transaction = function.buildTransaction(
                {
                    "from": account.address,
                    "gas": gas_estimate,
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": self.w3.eth.get_transaction_count(account.address),
                }
            )

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, agent_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(f"Vote cast successfully - TX: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            raise

    async def get_treasury_data(self) -> Dict[str, Any]:
        """Get treasury data"""
        try:
            treasury_data = {
                "total_value": 1500000,  # Mock data - replace with actual contract calls
                "allocations": {"XMRT": 0.4, "ETH": 0.3, "USDC": 0.2, "Other": 0.1},
                "historical": [
                    {"timestamp": datetime.now().timestamp() - 86400, "value": 1480000},
                    {"timestamp": datetime.now().timestamp(), "value": 1500000},
                ],
            }

            return treasury_data

        except Exception as e:
            logger.error(f"Error getting treasury data: {e}")
            return {}

    async def execute_trade(self, asset: str, action: str, amount: float) -> str:
        """Execute a trade"""
        try:
            logger.info(f"Executing trade: {action} {amount} {asset}")

            # Mock implementation - replace with actual DEX integration
            # This would integrate with Uniswap, 1inch, or other DEX protocols

            # Generate mock transaction hash
            import hashlib

            trade_data = f"{asset}{action}{amount}{datetime.now().timestamp()}"
            tx_hash = hashlib.sha256(trade_data.encode()).hexdigest()

            return f"0x{tx_hash[:64]}"

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise

    async def create_proposal(
        self, title: str, description: str, actions: List[Dict[str, Any]]
    ) -> str:
        """Create a governance proposal"""
        try:
            if "dao_governance" not in self.contracts:
                raise ValueError("Governance contract not available")

            # Get agent account
            agent_key = os.getenv("GOVERNANCE_AGENT_PRIVATE_KEY")
            if not agent_key:
                raise ValueError("Agent private key not configured")

            account = Account.from_key(agent_key)

            # Prepare proposal data
            targets = [
                action.get("target", "0x0000000000000000000000000000000000000000")
                for action in actions
            ]
            values = [action.get("value", 0) for action in actions]
            calldatas = [action.get("calldata", "0x") for action in actions]

            # Build transaction (mock implementation)
            logger.info(f"Creating proposal: {title}")

            # Generate mock transaction hash
            import hashlib

            proposal_data = f"{title}{description}{datetime.now().timestamp()}"
            tx_hash = hashlib.sha256(proposal_data.encode()).hexdigest()

            return f"0x{tx_hash[:64]}"

        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            raise

    async def validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate a proposal action"""
        try:
            # Basic validation
            required_fields = ["target", "value", "calldata"]

            for field in required_fields:
                if field not in action:
                    return False

            # Validate target address
            target = action["target"]
            if not Web3.isAddress(target):
                return False

            # Validate value
            value = action["value"]
            if not isinstance(value, (int, float)) or value < 0:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating action: {e}")
            return False

    async def store_analysis(self, data: Dict[str, Any]):
        """Store analysis data"""
        try:
            # In production, store in IPFS or decentralized storage
            logger.info(f"Storing analysis data for proposal {data.get('proposal_id')}")

        except Exception as e:
            logger.error(f"Error storing analysis: {e}")

    async def store_sentiment(self, data: Dict[str, Any]):
        """Store sentiment analysis data"""
        try:
            logger.info("Storing sentiment analysis data")

        except Exception as e:
            logger.error(f"Error storing sentiment: {e}")

    async def store_monitoring_data(self, data: Dict[str, Any]):
        """Store monitoring data"""
        try:
            logger.info("Storing monitoring data")

        except Exception as e:
            logger.error(f"Error storing monitoring data: {e}")

    async def store_optimization_results(self, data: Dict[str, Any]):
        """Store optimization results"""
        try:
            logger.info("Storing optimization results")

        except Exception as e:
            logger.error(f"Error storing optimization results: {e}")

    async def store_community_data(self, data: Dict[str, Any]):
        """Store community data"""
        try:
            logger.info("Storing community data")

        except Exception as e:
            logger.error(f"Error storing community data: {e}")

    async def get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user interaction history"""
        try:
            # Mock implementation
            return {
                "user_id": user_id,
                "interactions": 5,
                "last_interaction": datetime.now().isoformat(),
                "reputation": 0.8,
            }

        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return {}

    def switch_network(self, network: str):
        """Switch to a different network"""
        try:
            if network in self.networks:
                self.primary_network = network
                self.w3 = Web3(Web3.HTTPProvider(self.networks[network]["rpc_url"]))
                self.contracts = self.initialize_contracts()
                logger.info(f"Switched to {network} network")
            else:
                raise ValueError(f"Unknown network: {network}")

        except Exception as e:
            logger.error(f"Error switching network: {e}")
            raise

    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information"""
        return {
            "network": self.primary_network,
            "chain_id": self.networks[self.primary_network]["chain_id"],
            "connected": self.w3.isConnected(),
            "latest_block": self.w3.eth.block_number if self.w3.isConnected() else 0,
        }
