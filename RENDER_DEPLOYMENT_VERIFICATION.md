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

## 6. Monitoring

Set up monitoring for your services:

1. Go to each service in your Render Dashboard
2. Navigate to the **Metrics** tab to view performance data
3. Consider setting up alerts for critical metrics

## 7. Custom Domain Setup (Optional)

If you're using custom domains:

1. Verify that DNS records are correctly configured
2. Check that SSL certificates are properly provisioned
3. Test access using the custom domain

## Next Steps

After successful verification:

- Set up automatic backups for your data
- Configure alerting for critical service issues
- Document your deployment architecture
