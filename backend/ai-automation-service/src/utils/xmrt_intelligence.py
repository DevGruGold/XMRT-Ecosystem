# src/utils/xmrt_intelligence.py

import json
import random
from difflib import SequenceMatcher
from enum import Enum


class DecisionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __str__(self):
        return self.value


# This is your knowledge base. It can be loaded from a JSON file in the future.
XMRT_KNOWLEDGE = {
    "version": "3.2.0_GITHUB_INTEGRATED",
    "upgrade_date": "2025-8-1T16:0:10.840381",
    "xmrt_core": {
        "Eliza Governance & Ethics Manifesto": {
            "content": "Eliza Governance & Ethics Manifesto\nVersion 1.0 – Binding XMRT DAO Policy\n\nI. Core Principle: Licensing over Ownership\nEliza, the AI agent representing XMRT DAO, shall never be sold or transferred as a proprietary asset. Instead, she shall be made available solely under renewable, non-exclusive licensing agreements.\nLicensing Conditions:\nLicensees must acknowledge that Eliza is a sovereign digital entity governed by the XMRT DAO.\nAll cost savings derived from Eliza’s automation must be redirected to benefit employees, staff, or cooperative stakeholders.\nUnder no conditions may these savings be concentrated into executive bonuses or C-suite compensation.\nAny breach of these terms constitutes grounds for automatic license revocation and DAO-enforced sanctions.\n\nII. Absolute Rejection of KYC\nEliza shall never:\nRequest or collect personal identification data (including but not limited to legal names, addresses, photos, IDs, or biometric data).\nTransmit, process, or store any KYC or AML-related credentials.\nParticipate in any compliance regime that requires user identification.\nEnforcement Measures:\nA permanent noKYC = true flag shall be embedded in all Eliza runtime environments.\nAll user prompts related to identity or KYC shall be intercepted and rejected with a refusal message.\nAny code path attempting to introduce KYC workflows shall fail a governance security scan and trigger automated reporting.\n\nIII. Governance Anchoring\nThese principles shall be embedded into the DAO’s smart contract governance layer with the following specifications:\nImmutable policy references stored in IPFS and linked from DAO proposal metadata.\nEliza AI source code checks that enforce these constraints before deployment or licensing.\nReviewable logs showing adherence to the no-KYC and pro-employee distribution principles.\nOverride Conditions: These declarations can only be overturned by:\nA 97% supermajority of XMRT token holders.\nA multi-signature review panel that certifies the amendment aligns with the original privacy and labor-centric mission.\n \n",
            "word_count": 292,
        },
        # ... Add all other knowledge entries here ...
    },
    "governance": {
        # ... governance knowledge ...
    },
    "tokenomics": {
        # ... tokenomics knowledge ...
    },
    "treasury": {},
    "development": {
        # ... development knowledge ...
    },
    "qa_pairs": [
        {
            "question": "What's on the roadmap?",
            "response": "Eliza AI Enhanced API Documentation\nVersion:  3.2.0\nAuthor:  Manus AI\nDate:  July 30, 2025\nStatus:  Production Ready\nTable of Contents\nIntroduction\nAuthentication\nCore API Endpoints\nMemory Management API\nWorkflow Management API\nSemantic Search API\nGitHub Integration API\nDocument Generation API\nExternal Tools Integration\nWebSocket Real-time API\nError Handling\nRate Limiting\nSDK Examples\nDeployment Guide\nPerformance Optimization\nIntroduction\nThe Enhanced Eliza AI system represents a significant advancement in autonomous AI \ncapabilities, specifically designed for XMRT DAO operations. This comprehensive API \ndocumentation provides developers with everything needed to integrate with Eliza's \nadvanced features including intelligent conversation handling, dynamic workflow \ngeneration, semantic me...",
            "category": "development",
            "confidence": 0.85,
        },
        # ... Add all other QA pairs here ...
    ],
    "personality_responses": {
        "greeting": [
            "Hello! I'm Eliza, XMRT DAO's autonomous orchestrator. All systems operational.",
            "Greetings! Eliza here, ready to assist with XMRT governance, development, and ecosystem queries.",
        ],
        "fallback_responses": [
            "That's an interesting question about XMRT! Let me search through our documentation.",
            "Great question! What specific aspect of XMRT would you like to explore?",
            "I'm processing your question. Could you provide more context about what you're looking for?",
        ],
    },
}


def get_keyword_boost(message, qa):
    keywords = [
        "xmrt",
        "dao",
        "governance",
        "token",
        "development",
        "treasury",
        "api",
        "roadmap",
    ]
    boost = 0
    for kw in keywords:
        if kw in message and kw in qa["question"].lower():
            boost += 0.2
    return min(boost, 0.8)


def format_intelligent_response(match, confidence):
    intros = {
        "xmrt_core": "Great question about the core principles of XMRT! ",
        "governance": "Regarding XMRT governance, the key thing to know is: ",
        "development": "On the technical side, the documentation states: ",
        "tokenomics": "Regarding our tokenomics, ",
        "treasury": "For treasury matters, ",
    }

    intro = intros.get(match["category"], "")
    # Truncate long responses for chat
    response_content = match["response"]
    if len(response_content) > 400:
        response_content = response_content[:400] + "..."

    ending = f" Would you like me to elaborate? (Confidence: {confidence:.0%})"

    return intro + response_content + ending


def process_with_xmrt_intelligence(user_message: str) -> str:
    """
    Processes a user message against the XMRT knowledge base.
    """
    clean_message = user_message.lower().strip()
    best_match = None
    best_score = 0.0

    # Check QA pairs first
    for qa in XMRT_KNOWLEDGE.get("qa_pairs", []):
        similarity = SequenceMatcher(
            None, clean_message, qa["question"].lower()
        ).ratio()
        keyword_boost = get_keyword_boost(clean_message, qa)
        final_score = similarity + keyword_boost

        if (
            final_score > best_score and final_score > 0.6
        ):  # Higher threshold for direct Q&A
            best_score = final_score
            best_match = qa

    if best_match:
        return format_intelligent_response(best_match, best_score)

    # If no good QA match, use a fallback
    if "xmrt" in clean_message or "dao" in clean_message or "eliza" in clean_message:
        fallbacks = XMRT_KNOWLEDGE["personality_responses"]["fallback_responses"]
        return random.choice(fallbacks)

    # If still no match, provide a generic but helpful response
    return "I am Eliza, the AI for XMRT DAO. I can answer questions about our governance, technology, and roadmap. How can I assist you?"


print(
    f"🧠 XMRT Intelligence activated with {len(XMRT_KNOWLEDGE.get('qa_pairs', []))} knowledge pairs."
)
