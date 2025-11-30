# Eliza C-Suite Autonomous n8n Workflows

This directory contains the n8n workflow JSON files that provide Eliza with C-suite level autonomous capabilities. These workflows are integrated into the XMRT Ecosystem to enable advanced strategic decision-making, data analysis, and long-term memory management.

## Workflows

1.  **long_term_memory_agent.json**:
    *   **Source**: `ultimate-n8n-ai-workflows-main41/ultimate-n8n-ai-workflows-main/automation/AI Agent Chatbot + LONG TERM Memory + Note Storage + Telegram.json`
    *   **Capability**: Provides Eliza with persistent memory for strategic context and long-term planning. This is crucial for maintaining context across complex, multi-step operations.

2.  **data_analysis_agent.json**:
    *   **Source**: `ultimate-n8n-ai-workflows-main41/ultimate-n8n-ai-workflows-main/automation/Multi-AI Agent Chatbot for Postgres Supabase DB and QuickCharts + Tool Router.json`
    *   **Capability**: Enables Eliza to perform complex data analysis, query the ecosystem's database (Supabase/Postgres), and generate data visualizations (QuickCharts) for executive reporting and strategic insights.

## Integration Notes

These workflows are designed to be deployed on an n8n instance accessible by the XMRT Ecosystem's agent orchestration layer. The primary integration points are:
*   **Database**: The `data_analysis_agent` is configured for Postgres/Supabase, which aligns with the XMRT-Ecosystem's architecture. Connection details must be configured in the n8n instance.
*   **AI Agent**: The workflows use the LangChain Agent nodes, which will be exposed to Eliza's core reasoning engine.
*   **Tool Router**: The `data_analysis_agent` uses a tool router, allowing Eliza to dynamically select between querying the database and generating charts based on the user's request.

