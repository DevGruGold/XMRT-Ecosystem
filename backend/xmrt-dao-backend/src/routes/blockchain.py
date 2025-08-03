from flask import Blueprint, jsonify, request
from web3 import Web3
import os
from dotenv import load_dotenv
import json

load_dotenv()

blockchain_bp = Blueprint("blockchain", __name__)

# Blockchain configuration
SEPOLIA_RPC_URL = os.getenv(
    "SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
)
XMRT_CONTRACT_ADDRESS = os.getenv(
    "XMRT_CONTRACT_ADDRESS", "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
)
CHAIN_ID = int(os.getenv("CHAIN_ID", "11155111"))

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))

# XMRT Contract ABI (simplified for key functions)
XMRT_ABI = [
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalStaked",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "userStakes",
        "outputs": [
            {"internalType": "uint128", "name": "amount", "type": "uint128"},
            {"internalType": "uint64", "name": "timestamp", "type": "uint64"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "stake",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "unstake",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# Initialize contract
contract = w3.eth.contract(address=XMRT_CONTRACT_ADDRESS, abi=XMRT_ABI)


@blockchain_bp.route("/contract-info", methods=["GET"])
def get_contract_info():
    """Get basic contract information"""
    try:
        total_supply = contract.functions.totalSupply().call()
        total_staked = contract.functions.totalStaked().call()

        return jsonify(
            {
                "success": True,
                "data": {
                    "contract_address": XMRT_CONTRACT_ADDRESS,
                    "total_supply": str(total_supply),
                    "total_staked": str(total_staked),
                    "chain_id": CHAIN_ID,
                    "network": "Sepolia Testnet",
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route("/balance/<address>", methods=["GET"])
def get_balance(address):
    """Get XMRT token balance for an address"""
    try:
        if not w3.is_address(address):
            return jsonify({"success": False, "error": "Invalid address format"}), 400

        balance = contract.functions.balanceOf(address).call()

        return jsonify(
            {
                "success": True,
                "data": {
                    "address": address,
                    "balance": str(balance),
                    "balance_formatted": str(balance / 10**18),  # Convert from wei
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route("/stake-info/<address>", methods=["GET"])
def get_stake_info(address):
    """Get staking information for an address"""
    try:
        if not w3.is_address(address):
            return jsonify({"success": False, "error": "Invalid address format"}), 400

        stake_info = contract.functions.userStakes(address).call()

        return jsonify(
            {
                "success": True,
                "data": {
                    "address": address,
                    "staked_amount": str(stake_info[0]),
                    "staked_amount_formatted": str(stake_info[0] / 10**18),
                    "stake_timestamp": stake_info[1],
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@blockchain_bp.route("/network-status", methods=["GET"])
def get_network_status():
    """Get network connection status"""
    try:
        is_connected = w3.is_connected()
        latest_block = w3.eth.block_number if is_connected else None

        return jsonify(
            {
                "success": True,
                "data": {
                    "connected": is_connected,
                    "latest_block": latest_block,
                    "chain_id": CHAIN_ID,
                    "network": "Sepolia Testnet",
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
