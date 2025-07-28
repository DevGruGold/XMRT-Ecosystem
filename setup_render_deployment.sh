#!/bin/bash
# XMRT-Ecosystem Render Deployment Setup Script
# This script prepares the repository for deployment on Render

# Display banner
echo "=================================="
echo " XMRT-Ecosystem Render Deployment "
echo "=================================="
echo ""

# Ensure render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "Error: render.yaml not found!"
    echo "Please make sure you have the render.yaml file in the root directory."
    exit 1
else
    echo "✅ render.yaml found"
fi

# Check for deployment guide
if [ ! -f "RENDER_DEPLOYMENT_GUIDE.md" ]; then
    echo "Warning: RENDER_DEPLOYMENT_GUIDE.md not found!"
    echo "Consider creating a deployment guide for easier reference."
fi

# Check for Python requirements in backend services
if [ ! -f "backend/eliza-backend/requirements.txt" ]; then
    echo "Error: Missing requirements.txt in backend/eliza-backend"
    exit 1
else
    echo "✅ eliza-backend requirements.txt found"
fi

if [ ! -f "backend/ai-automation-service/requirements.txt" ]; then
    echo "Error: Missing requirements.txt in backend/ai-automation-service"
    exit 1
else
    echo "✅ ai-automation-service requirements.txt found"
fi

# Check for the unified frontend
if [ ! -d "frontend/xmrt-unified-cashdapp" ]; then
    echo "Error: Unified frontend not found at frontend/xmrt-unified-cashdapp"
    exit 1
else
    echo "✅ unified frontend found"
fi

# Check for package.json in the frontend
if [ ! -f "frontend/xmrt-unified-cashdapp/package.json" ]; then
    echo "Error: Missing package.json in frontend/xmrt-unified-cashdapp"
    exit 1
else
    echo "✅ frontend package.json found"
fi

# Create directories if they don't exist
mkdir -p logs

# Create a simple deployment verification file
cat > RENDER_DEPLOYMENT_VERIFICATION.md << 'EOL'
# XMRT-Ecosystem Deployment Verification

To verify that your XMRT-Ecosystem deployment on Render is working correctly, follow these steps:

## 1. Verify Services

Check that all three services are up and running:

- **xmrt-frontend**: https://xmrt-frontend.onrender.com
- **xmrt-eliza-automation**: https://xmrt-eliza-automation.onrender.com
- **xmrt-eliza-backend**: https://xmrt-eliza-backend.onrender.com

## 2. Health Check

Verify that the health check endpoint is responding:

```bash
curl https://xmrt-eliza-backend.onrender.com/api/eliza/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "eliza-backend",
  "version": "1.0.0"
}
```

## 3. Frontend Access

Open the frontend URL in your browser and confirm:

- The dashboard loads correctly
- You can navigate between different sections
- The Eliza AI interface is available

## 4. Eliza AI Interaction

Test the Eliza AI functionality:

1. Open the AI chat interface
2. Send a test message: "Hello Eliza, what can you do?"
3. Verify that Eliza responds appropriately

## 5. Environment Variable Check

If any functionality is not working, verify that all required environment variables are set correctly in your Render environment.

For a complete list of required variables, refer to the RENDER_DEPLOYMENT_GUIDE.md file.
EOL

echo "✅ Created deployment verification guide"

# Create a GitHub Actions workflow for deployment (optional)
mkdir -p .github/workflows

# Success message
echo ""
echo "✅ Deployment setup complete!"
echo "You can now deploy to Render using the instructions in RENDER_DEPLOYMENT_GUIDE.md"
echo ""
