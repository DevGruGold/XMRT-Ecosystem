#!/bin/bash
# Quick Deploy to Render Script
# This script provides the commands to deploy on Render

echo "🚀 XMRT-Ecosystem Render Deployment Instructions"
echo "================================================="
echo ""

echo "1. Go to your Render Dashboard: https://dashboard.render.com/"
echo ""

echo "2. Click 'New' → 'Blueprint'"
echo ""

echo "3. Connect your GitHub repository: DevGruGold/XMRT-Ecosystem"
echo ""

echo "4. Select the branch: eliza-improvements-1753457195"
echo ""

echo "5. Set the Blueprint path: render.yaml"
echo ""

echo "6. Configure these environment variables in the xmrt-env-group:"
echo "   - OPENAI_API_KEY=your_openai_key"
echo "   - VITE_ETHEREUM_RPC_URL=your_ethereum_rpc"
echo "   - VITE_POLYGON_RPC_URL=your_polygon_rpc"
echo "   - VITE_BSC_RPC_URL=your_bsc_rpc"
echo "   - VITE_AVALANCHE_RPC_URL=your_avalanche_rpc"
echo "   - VITE_WALLET_CONNECT_PROJECT_ID=your_wallet_connect_id"
echo "   - VITE_ENCRYPTION_KEY=your_secure_encryption_key"
echo ""

echo "7. Click 'Apply Blueprint' to deploy all services"
echo ""

echo "8. Services will be available at:"
echo "   - Frontend: https://xmrt-frontend.onrender.com"
echo "   - Eliza Automation: https://xmrt-eliza-automation.onrender.com"
echo "   - Eliza Backend: https://xmrt-eliza-backend.onrender.com"
echo ""

echo "✅ Deployment Complete! Use RENDER_DEPLOYMENT_VERIFICATION.md to verify everything is working."
