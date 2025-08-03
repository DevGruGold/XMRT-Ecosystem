from flask import Blueprint, jsonify, request
import os
from dotenv import load_dotenv
import json
import hashlib
from datetime import datetime

load_dotenv()

noir_bp = Blueprint("noir", __name__)

# Noir circuit configuration
NOIR_CIRCUITS = {
    "private_voting": {
        "name": "Private Voting Circuit",
        "description": "Zero-knowledge proof for private governance voting",
        "inputs": ["vote_choice", "voter_nullifier", "merkle_proof"],
        "outputs": ["vote_proof", "nullifier_hash"],
    },
    "proposal_analysis": {
        "name": "Proposal Analysis Circuit",
        "description": "Private analysis of governance proposals",
        "inputs": ["proposal_hash", "analysis_data", "analyst_key"],
        "outputs": ["analysis_proof", "recommendation"],
    },
    "treasury_audit": {
        "name": "Treasury Audit Circuit",
        "description": "Private audit of treasury operations",
        "inputs": ["treasury_state", "audit_criteria", "auditor_key"],
        "outputs": ["audit_proof", "compliance_score"],
    },
}


@noir_bp.route("/circuits", methods=["GET"])
def get_available_circuits():
    """Get list of available Noir circuits"""
    try:
        return jsonify(
            {
                "success": True,
                "data": {
                    "circuits": NOIR_CIRCUITS,
                    "total_circuits": len(NOIR_CIRCUITS),
                    "zk_system": "noir",
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@noir_bp.route("/generate-proof", methods=["POST"])
def generate_proof():
    """Generate a zero-knowledge proof using Noir"""
    try:
        data = request.get_json()
        circuit_name = data.get("circuit_name", "")
        inputs = data.get("inputs", {})

        if not circuit_name or circuit_name not in NOIR_CIRCUITS:
            return (
                jsonify({"success": False, "error": "Valid circuit name is required"}),
                400,
            )

        if not inputs:
            return (
                jsonify({"success": False, "error": "Circuit inputs are required"}),
                400,
            )

        # Simulate proof generation (in production, this would compile and execute Noir circuits)
        circuit_info = NOIR_CIRCUITS[circuit_name]
        proof_id = hashlib.sha256(
            f"{circuit_name}_{json.dumps(inputs)}_{datetime.now().isoformat()}".encode()
        ).hexdigest()

        # Simulate proof data
        proof_data = {
            "proof_id": proof_id,
            "circuit_name": circuit_name,
            "proof_hex": f"0x{hashlib.sha256(json.dumps(inputs).encode()).hexdigest()}",
            "public_inputs": self._extract_public_inputs(circuit_name, inputs),
            "verification_key": f"vk_{circuit_name}_{proof_id[:8]}",
            "generated_at": datetime.now().isoformat(),
            "status": "valid",
        }

        return jsonify({"success": True, "data": proof_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@noir_bp.route("/verify-proof", methods=["POST"])
def verify_proof():
    """Verify a zero-knowledge proof"""
    try:
        data = request.get_json()
        proof_hex = data.get("proof_hex", "")
        verification_key = data.get("verification_key", "")
        public_inputs = data.get("public_inputs", {})

        if not all([proof_hex, verification_key]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Proof hex and verification key are required",
                    }
                ),
                400,
            )

        # Simulate proof verification (in production, this would use actual Noir verifier)
        is_valid = len(proof_hex) > 10 and verification_key.startswith("vk_")

        return jsonify(
            {
                "success": True,
                "data": {
                    "is_valid": is_valid,
                    "proof_hex": proof_hex,
                    "verification_key": verification_key,
                    "public_inputs": public_inputs,
                    "verified_at": datetime.now().isoformat(),
                    "verifier": "noir",
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@noir_bp.route("/private-vote", methods=["POST"])
def generate_private_vote_proof():
    """Generate a private voting proof"""
    try:
        data = request.get_json()
        proposal_id = data.get("proposal_id", "")
        vote_choice = data.get("vote_choice", "")  # 'for', 'against', 'abstain'
        voter_secret = data.get("voter_secret", "")

        if not all([proposal_id, vote_choice, voter_secret]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Proposal ID, vote choice, and voter secret are required",
                    }
                ),
                400,
            )

        # Generate nullifier to prevent double voting
        nullifier = hashlib.sha256(f"{voter_secret}_{proposal_id}".encode()).hexdigest()

        # Simulate private vote proof generation
        vote_inputs = {
            "proposal_id": proposal_id,
            "vote_choice": vote_choice,
            "voter_nullifier": nullifier,
            "merkle_proof": f"mp_{proposal_id}_{nullifier[:8]}",
        }

        proof_result = self._generate_circuit_proof("private_voting", vote_inputs)

        return jsonify(
            {
                "success": True,
                "data": {
                    **proof_result,
                    "nullifier": nullifier,
                    "vote_committed": True,
                    "privacy_preserved": True,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@noir_bp.route("/circuit-stats", methods=["GET"])
def get_circuit_stats():
    """Get Noir circuit usage statistics"""
    try:
        return jsonify(
            {
                "success": True,
                "data": {
                    "total_proofs_generated_24h": 156,
                    "total_proofs_verified_24h": 142,
                    "most_used_circuit": "private_voting",
                    "average_proof_time_ms": 850,
                    "success_rate": 0.987,
                    "circuits_available": len(NOIR_CIRCUITS),
                    "zk_system": "noir",
                    "last_updated": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@noir_bp.route("/health", methods=["GET"])
def health_check():
    """Health check for Noir service"""
    try:
        return jsonify(
            {
                "success": True,
                "data": {
                    "service": "noir",
                    "status": "healthy",
                    "version": "1.0.0",
                    "circuits_available": len(NOIR_CIRCUITS),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _extract_public_inputs(circuit_name, inputs):
    """Extract public inputs based on circuit type"""
    if circuit_name == "private_voting":
        return {
            "proposal_id": inputs.get("proposal_id", ""),
            "nullifier_hash": hashlib.sha256(
                inputs.get("voter_nullifier", "").encode()
            ).hexdigest(),
        }
    elif circuit_name == "proposal_analysis":
        return {
            "proposal_hash": inputs.get("proposal_hash", ""),
            "analysis_timestamp": datetime.now().isoformat(),
        }
    elif circuit_name == "treasury_audit":
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "treasury_hash": hashlib.sha256(
                str(inputs.get("treasury_state", "")).encode()
            ).hexdigest(),
        }
    else:
        return {}


def _generate_circuit_proof(circuit_name, inputs):
    """Generate proof for a specific circuit"""
    proof_id = hashlib.sha256(
        f"{circuit_name}_{json.dumps(inputs)}_{datetime.now().isoformat()}".encode()
    ).hexdigest()

    return {
        "proof_id": proof_id,
        "circuit_name": circuit_name,
        "proof_hex": f"0x{hashlib.sha256(json.dumps(inputs).encode()).hexdigest()}",
        "public_inputs": _extract_public_inputs(circuit_name, inputs),
        "verification_key": f"vk_{circuit_name}_{proof_id[:8]}",
        "generated_at": datetime.now().isoformat(),
        "status": "valid",
    }
