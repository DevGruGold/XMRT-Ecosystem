# launcher.py - The Production Web Server & API for Eliza

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os

# --- Import Core Logic & Utilities from other files ---
from main import AIAutomationService
from src.utils.diagnostics import (
    run_internal_ai_diagnostics,
)  # MOVED to a separate file
from src.utils.xmrt_intelligence import (
    process_with_xmrt_intelligence,
)  # MOVED to a separate file

# --- Basic Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Eliza AI Automation Service",
    version="3.3.2",  # Version bump for the refactor!
    description="Live Production Instance of Eliza's Core Agent System",
)


# --- Pydantic Models for our Chat API ---
class ChatMessage(BaseModel):
    message: str


# --- API Endpoints ---


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """
    Serves the main chat interface HTML file.
    """
    try:
        # Assumes index.html is in a 'static' subfolder relative to where the app is run
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        logger.error(
            "FATAL: static/index.html not found! The chat interface cannot be served."
        )
        return HTMLResponse(
            content="<h1>Error 500: Interface file not found.</h1><p>Server is running, but the admin needs to add the index.html file.</p>",
            status_code=500,
        )


@app.post("/api/chat")
async def handle_chat(chat_message: ChatMessage):
    """
    This is the dedicated endpoint for handling chat messages.
    It uses the XMRT Intelligence system to generate a response.
    """
    user_message = chat_message.message
    logger.info(f"Received chat message: {user_message}")

    # Check for special diagnostic command
    if user_message.strip().lower() in [
        "run internal ai diagnostics",
        "ai diagnostics",
        "test ai keys",
        "show ai api health",
    ]:
        diagnostics = run_internal_ai_diagnostics()
        return {"response": f"🔬 AI API Diagnostics:\n\n{diagnostics}"}

    # Use the dedicated XMRT Intelligence function for all other queries
    response = process_with_xmrt_intelligence(user_message)

    return {"response": response}


@app.get("/health", status_code=200)
async def health_check():
    """A simple health check endpoint for Render to monitor service availability."""
    return {
        "status": "healthy",
        "message": "Eliza Agent Service is online and responsive.",
    }


@app.head("/")
def root_head():
    """Handles HEAD requests to the root, often used for health checks."""
    return {}


# --- FastAPI Startup Event ---
@app.on_event("startup")
async def on_startup():
    """
    When the server starts, this function launches the main AI agent logic
    as a background task, so it doesn't block the web server.
    """
    logger.info("Application startup: Launching background AIAutomationService.")
    # This is where your core autonomous agent from main.py gets kicked off
    service = AIAutomationService()
    asyncio.create_task(service.start_automation())
    logger.info("✅ Background agent service has been scheduled to run.")


# --- Local Development Runner ---
if __name__ == "__main__":
    # This block only runs when you execute `python launcher.py` directly
    # It will NOT run when started by Gunicorn in production
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting Uvicorn server for local development on port {port}...")
    uvicorn.run("launcher:app", host="0.0.0.0", port=port, reload=True)
