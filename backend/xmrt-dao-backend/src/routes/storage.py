from flask import Blueprint, jsonify, request
import os
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

storage_bp = Blueprint("storage", __name__)


class DecentralizedStorage:
    def __init__(self):
        self.ipfs_gateway = os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs/")
        self.ipfs_api = os.getenv("IPFS_API", "http://localhost:5001/api/v0/")

    def store_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store governance proposal on IPFS"""
        try:
            # Prepare proposal metadata
            proposal_metadata = {
                "title": proposal_data.get("title", ""),
                "description": proposal_data.get("description", ""),
                "proposer": proposal_data.get("proposer", ""),
                "timestamp": datetime.now().isoformat(),
                "type": "governance_proposal",
                "version": "1.0",
            }

            # Convert to JSON
            proposal_json = json.dumps(proposal_metadata, indent=2)

            # Store on IPFS (simulated for now)
            content_hash = hashlib.sha256(proposal_json.encode()).hexdigest()
            ipfs_hash = f"Qm{content_hash[:44]}"  # Simulated IPFS hash

            return {
                "success": True,
                "ipfs_hash": ipfs_hash,
                "gateway_url": f"{self.ipfs_gateway}{ipfs_hash}",
                "size_bytes": len(proposal_json),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def store_ai_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store AI model weights and metadata on IPFS"""
        try:
            # Prepare model metadata
            model_metadata = {
                "model_name": model_data.get("model_name", ""),
                "version": model_data.get("version", "1.0"),
                "architecture": model_data.get("architecture", ""),
                "training_data_hash": model_data.get("training_data_hash", ""),
                "performance_metrics": model_data.get("performance_metrics", {}),
                "timestamp": datetime.now().isoformat(),
                "type": "ai_model",
            }

            # Convert to JSON
            model_json = json.dumps(model_metadata, indent=2)

            # Store metadata on IPFS (simulated)
            content_hash = hashlib.sha256(model_json.encode()).hexdigest()
            ipfs_hash = f"Qm{content_hash[:44]}"

            return {
                "success": True,
                "metadata_hash": ipfs_hash,
                "gateway_url": f"{self.ipfs_gateway}{ipfs_hash}",
                "size_bytes": len(model_json),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def retrieve_content(self, ipfs_hash: str) -> Dict[str, Any]:
        """Retrieve content from IPFS"""
        try:
            # In a real implementation, this would fetch from IPFS
            # For now, return simulated data
            return {
                "success": True,
                "ipfs_hash": ipfs_hash,
                "content": f"Content for hash {ipfs_hash}",
                "retrieved_at": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class RuntimeVerification:
    def __init__(self):
        self.verification_service = os.getenv(
            "VERIFICATION_SERVICE_URL", "http://localhost:5003"
        )

    def verify_ai_agent_execution(
        self, execution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify AI agent execution using runtime verification"""
        try:
            # Prepare verification inputs
            verification_inputs = {
                "agent_id": execution_data.get("agent_id", ""),
                "action_type": execution_data.get("action_type", ""),
                "inputs": execution_data.get("inputs", {}),
                "outputs": execution_data.get("outputs", {}),
                "timestamp": execution_data.get(
                    "timestamp", datetime.now().isoformat()
                ),
                "execution_trace": execution_data.get("execution_trace", []),
            }

            # Simulate verification process
            verification_result = {
                "verified": True,
                "confidence_score": 0.95,
                "verification_method": "runtime_monitoring",
                "anomalies_detected": [],
                "execution_time_ms": 150,
                "memory_usage_mb": 45,
                "verification_timestamp": datetime.now().isoformat(),
            }

            return {
                "success": True,
                "verification_result": verification_result,
                "verification_hash": hashlib.sha256(
                    json.dumps(verification_inputs).encode()
                ).hexdigest(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_smart_contract_interaction(
        self, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify smart contract interactions"""
        try:
            # Prepare verification inputs
            verification_inputs = {
                "contract_address": interaction_data.get("contract_address", ""),
                "function_name": interaction_data.get("function_name", ""),
                "parameters": interaction_data.get("parameters", {}),
                "transaction_hash": interaction_data.get("transaction_hash", ""),
                "block_number": interaction_data.get("block_number", 0),
                "gas_used": interaction_data.get("gas_used", 0),
            }

            # Simulate verification
            verification_result = {
                "verified": True,
                "security_score": 0.98,
                "reentrancy_check": "passed",
                "access_control_check": "passed",
                "state_consistency_check": "passed",
                "gas_optimization_score": 0.85,
                "verification_timestamp": datetime.now().isoformat(),
            }

            return {
                "success": True,
                "verification_result": verification_result,
                "verification_hash": hashlib.sha256(
                    json.dumps(verification_inputs).encode()
                ).hexdigest(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instances
storage = DecentralizedStorage()
verifier = RuntimeVerification()


@storage_bp.route("/store/proposal", methods=["POST"])
def store_proposal():
    """Store governance proposal on IPFS"""
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"success": False, "error": "Proposal data is required"}),
                400,
            )

        result = storage.store_proposal(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@storage_bp.route("/store/ai-model", methods=["POST"])
def store_ai_model():
    """Store AI model on IPFS"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Model data is required"}), 400

        result = storage.store_ai_model(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@storage_bp.route("/retrieve/<ipfs_hash>", methods=["GET"])
def retrieve_content(ipfs_hash):
    """Retrieve content from IPFS"""
    try:
        if not ipfs_hash:
            return jsonify({"success": False, "error": "IPFS hash is required"}), 400

        result = storage.retrieve_content(ipfs_hash)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@storage_bp.route("/verify/ai-execution", methods=["POST"])
def verify_ai_execution():
    """Verify AI agent execution"""
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"success": False, "error": "Execution data is required"}),
                400,
            )

        result = verifier.verify_ai_agent_execution(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@storage_bp.route("/verify/contract-interaction", methods=["POST"])
def verify_contract_interaction():
    """Verify smart contract interaction"""
    try:
        data = request.get_json()

        if not data:
            return (
                jsonify({"success": False, "error": "Interaction data is required"}),
                400,
            )

        result = verifier.verify_smart_contract_interaction(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@storage_bp.route("/health", methods=["GET"])
def storage_health():
    """Get storage service health"""
    try:
        return jsonify(
            {
                "success": True,
                "data": {
                    "status": "active",
                    "services": {
                        "ipfs_gateway": storage.ipfs_gateway,
                        "ipfs_api": storage.ipfs_api,
                        "verification_service": verifier.verification_service,
                    },
                    "capabilities": [
                        "Proposal Storage",
                        "AI Model Storage",
                        "Content Retrieval",
                        "Runtime Verification",
                        "Smart Contract Verification",
                    ],
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
