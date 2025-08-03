# src/utils/diagnostics.py

import os
import requests


def run_internal_ai_diagnostics():
    """Checks the status of all configured AI provider API keys."""
    results = {}

    # --- Check OpenAI ---
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            r = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {openai_key}"},
                timeout=8,
            )
            results["OpenAI"] = (
                f"{r.status_code} {'✅' if r.status_code == 200 else '❌'}"
            )
        except Exception as ex:
            results["OpenAI"] = f"ERROR: {ex}"
    else:
        results["OpenAI"] = "❌ No key"

    # --- Check Anthropic ---
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            # Note: A 400 can be a success for a GET request if auth is valid but method is wrong
            r = requests.get(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
                timeout=8,
            )
            results["Anthropic"] = (
                f"{r.status_code} {'✅' if r.status_code in [200, 400, 405] else '❌'}"
            )
        except Exception as ex:
            results["Anthropic"] = f"ERROR: {ex}"
    else:
        results["Anthropic"] = "❌ No key"

    # --- Check Gemini ---
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        try:
            r = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}",
                timeout=8,
            )
            results["Gemini"] = (
                f"{r.status_code} {'✅' if r.status_code == 200 else '❌'}"
            )
        except Exception as ex:
            results["Gemini"] = f"ERROR: {ex}"
    else:
        results["Gemini"] = "❌ No key"

    # --- Check HuggingFace ---
    hf_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
    if hf_key:
        try:
            r = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {hf_key}"},
                timeout=8,
            )
            results["HuggingFace"] = (
                f"{r.status_code} {'✅' if r.status_code == 200 else '❌'}"
            )
        except Exception as ex:
            results["HuggingFace"] = f"ERROR: {ex}"
    else:
        results["HuggingFace"] = "❌ No key"

    # --- Check Web3 Provider ---
    web3_url = os.environ.get("WEB3_PROVIDER_URL")
    if web3_url:
        results["WEB3_PROVIDER_URL"] = "✅ Set"
    else:
        results["WEB3_PROVIDER_URL"] = "❌ Not set"

    output = "\n".join([f"- {svc}: {stat}" for svc, stat in results.items()])
    return output
