
# 🚀 XMRT-Ecosystem Eliza Deployment on Render

This guide provides step-by-step instructions for deploying the XMRT-Ecosystem with ElizaOS AI integration on Render.

## Prerequisites

- A Render account ([Sign up](https://render.com/signup) if you don't have one)
- A GitHub account connected to Render
- API keys for required services (OpenAI, Anthropic, etc.)
- Blockchain RPC URLs (Ethereum, Polygon, BSC, Avalanche)

## Deployment Steps

### 1. Fork the Repository

If you haven't already, fork the [XMRT-Ecosystem repository](https://github.com/DevGruGold/XMRT-Ecosystem) to your GitHub account.

### 2. Deploy with Blueprint

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Click the **New** button and select **Blueprint**
3. Connect to your GitHub account if you haven't already
4. Select the forked repository
5. Give your Blueprint a name (e.g., "xmrt-ecosystem")
6. Click **Apply Blueprint**

### 3. Configure Environment Variables

After applying the Blueprint, you need to set up the environment variables:

1. Navigate to the **Environment Groups** section
2. Select the `xmrt-env-group` that was created
3. Add the following environment variables (replace with your actual values):
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `VITE_ETHEREUM_RPC_URL`: Your Ethereum RPC URL
   - `VITE_POLYGON_RPC_URL`: Your Polygon RPC URL
   - `VITE_BSC_RPC_URL`: Your BSC RPC URL
   - `VITE_AVALANCHE_RPC_URL`: Your Avalanche RPC URL
   - `VITE_WALLET_CONNECT_PROJECT_ID`: Your WalletConnect Project ID
   - `VITE_MORALIS_API_KEY`: Your Moralis API key
   - `VITE_ALCHEMY_API_KEY`: Your Alchemy API key
   - `VITE_COINGECKO_API_KEY`: Your CoinGecko API key
   - `VITE_ENCRYPTION_KEY`: A secure encryption key

4. Click **Save Changes**

### 4. Verify Deployment

1. Once all services are deployed, navigate to the `xmrt-frontend` service URL
2. You should see the XMRT Dashboard with Eliza AI integration
3. Test the Eliza AI functionality by interacting with the chatbot

### 5. Set Up Custom Domain (Optional)

1. Go to each service in your Render Dashboard
2. Navigate to the **Settings** tab
3. In the **Custom Domain** section, click **Add Custom Domain**
4. Follow the instructions to configure your domain

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check the build logs for specific errors
   - Ensure all dependencies are correctly specified
   - Verify that the correct Node.js and Python versions are being used

2. **Environment Variable Issues**:
   - Double-check that all required environment variables are set correctly
   - Make sure API keys are valid

3. **Service Connection Problems**:
   - Verify that the services can communicate with each other
   - Check that the VITE_API_BASE_URL and ELIZA_AI_ENDPOINT variables are correct

## Support

If you encounter any issues, please:

1. Check the Render logs for specific error messages
2. Consult the [Render Documentation](https://render.com/docs)
3. Open an issue on the [XMRT-Ecosystem GitHub repository](https://github.com/DevGruGold/XMRT-Ecosystem/issues)

---

**Note**: This deployment configuration leverages Render's Blueprint feature to deploy all components of the XMRT-Ecosystem, including the ElizaOS autonomous AI agent system.
