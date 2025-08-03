from flask import Blueprint, jsonify, request
from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import json

load_dotenv()

ai_agents_bp = Blueprint("ai_agents", __name__)

# Blockchain configuration
SEPOLIA_RPC_URL = os.getenv(
    "SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
)
XMRT_CONTRACT_ADDRESS = os.getenv(
    "XMRT_CONTRACT_ADDRESS", "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
)
CHAIN_ID = int(os.getenv("CHAIN_ID", "11155111"))

# AI Agent private keys (TEST KEYS ONLY - DO NOT USE IN PRODUCTION)
GOVERNANCE_AGENT_KEY = os.getenv("GOVERNANCE_AGENT_PRIVATE_KEY")
TREASURY_AGENT_KEY = os.getenv("TREASURY_AGENT_PRIVATE_KEY")
COMMUNITY_AGENT_KEY = os.getenv("COMMUNITY_AGENT_PRIVATE_KEY")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))

# AI Agent configuration
AI_AGENTS = {
    "governance": {
        "name": "Governance Agent",
        "description": "Handles proposal processing and voting operations",
        "private_key": GOVERNANCE_AGENT_KEY,
        "roles": ["ADMIN_ROLE", "ORACLE_ROLE"],
    },
    "treasury": {
        "name": "Treasury Agent",
        "description": "Manages financial operations and yield optimization",
        "private_key": TREASURY_AGENT_KEY,
        "roles": ["ORACLE_ROLE"],
    },
    "community": {
        "name": "Community Agent",
        "description": "Handles community interactions and support",
        "private_key": COMMUNITY_AGENT_KEY,
        "roles": [],
    },
}


def get_agent_account(agent_type):
    """Get account object for an AI agent"""
    if agent_type not in AI_AGENTS:
        return None

    private_key = AI_AGENTS[agent_type]["private_key"]
    if not private_key:
        return None

    return Account.from_key(private_key)


def get_agent_address(agent_type):
    """Get address for an AI agent"""
    account = get_agent_account(agent_type)
    return account.address if account else None


@ai_agents_bp.route("/agents", methods=["GET"])
def list_agents():
    """List all AI agents and their information"""
    try:
        agents_info = {}

        for agent_type, config in AI_AGENTS.items():
            account = get_agent_account(agent_type)
            address = account.address if account else None

            # Get ETH balance
            eth_balance = 0
            if address and w3.is_connected():
                try:
                    eth_balance = w3.eth.get_balance(address)
                except:
                    pass

            agents_info[agent_type] = {
                "name": config["name"],
                "description": config["description"],
                "address": address,
                "eth_balance": str(eth_balance),
                "eth_balance_formatted": (
                    str(eth_balance / 10**18) if eth_balance else "0"
                ),
                "roles": config["roles"],
                "configured": address is not None,
            }

        return jsonify(
            {
                "success": True,
                "data": {
                    "agents": agents_info,
                    "total_agents": len(AI_AGENTS),
                    "network": "Sepolia Testnet",
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_agents_bp.route("/agent/<agent_type>", methods=["GET"])
def get_agent_info(agent_type):
    """Get detailed information about a specific AI agent"""
    try:
        if agent_type not in AI_AGENTS:
            return jsonify({"success": False, "error": "Invalid agent type"}), 400

        config = AI_AGENTS[agent_type]
        account = get_agent_account(agent_type)
        address = account.address if account else None

        # Get balances
        eth_balance = 0
        if address and w3.is_connected():
            try:
                eth_balance = w3.eth.get_balance(address)
            except:
                pass

        return jsonify(
            {
                "success": True,
                "data": {
                    "type": agent_type,
                    "name": config["name"],
                    "description": config["description"],
                    "address": address,
                    "eth_balance": str(eth_balance),
                    "eth_balance_formatted": (
                        str(eth_balance / 10**18) if eth_balance else "0"
                    ),
                    "roles": config["roles"],
                    "configured": address is not None,
                    "network": "Sepolia Testnet",
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_agents_bp.route("/agent/<agent_type>/generate-wallet", methods=["POST"])
def generate_agent_wallet(agent_type):
    """Generate a new wallet for an AI agent (development only)"""
    try:
        if agent_type not in AI_AGENTS:
            return jsonify({"success": False, "error": "Invalid agent type"}), 400

        # Generate new account
        account = Account.create()

        return jsonify(
            {
                "success": True,
                "data": {
                    "agent_type": agent_type,
                    "address": account.address,
                    "private_key": account.key.hex(),
                    "warning": "This is a test wallet. Do not use in production or with real funds.",
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_agents_bp.route("/agent/<agent_type>/sign-message", methods=["POST"])
def sign_message(agent_type):
    """Sign a message with an AI agent's private key"""
    try:
        if agent_type not in AI_AGENTS:
            return jsonify({"success": False, "error": "Invalid agent type"}), 400

        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        account = get_agent_account(agent_type)
        if not account:
            return (
                jsonify({"success": False, "error": "Agent wallet not configured"}),
                400,
            )

        # Sign the message
        signed_message = account.sign_message(message.encode())

        return jsonify(
            {
                "success": True,
                "data": {
                    "agent_type": agent_type,
                    "message": message,
                    "signature": signed_message.signature.hex(),
                    "signer_address": account.address,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_agents_bp.route("/funding-instructions", methods=["GET"])
def get_funding_instructions():
    """Get instructions for funding AI agent wallets"""
    try:
        agents_addresses = {}
        for agent_type in AI_AGENTS:
            address = get_agent_address(agent_type)
            if address:
                agents_addresses[agent_type] = address

        return jsonify(
            {
                "success": True,
                "data": {
                    "network": "Sepolia Testnet",
                    "faucets": [
                        "https://faucets.chain.link/sepolia",
                        "https://sepolia-faucet.pk910.de/",
                        "https://www.alchemy.com/faucets/ethereum-sepolia",
                    ],
                    "agents": agents_addresses,
                    "instructions": [
                        "1. Visit one of the Sepolia faucets listed above",
                        "2. Enter the agent wallet address",
                        "3. Request test ETH (usually 0.1-0.5 ETH per request)",
                        "4. Wait for the transaction to confirm",
                        "5. Verify the balance using the /agent/{agent_type} endpoint",
                    ],
                    "warning": "These are test wallets on Sepolia testnet. Do not send real ETH or tokens.",
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
