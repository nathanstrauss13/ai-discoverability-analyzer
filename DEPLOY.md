# Deploying to Render

This guide will help you deploy the AI Discoverability Analyzer to Render.

## Prerequisites

1. A [Render account](https://render.com/)
2. Your Anthropic API key

## Deployment Steps

### Option 1: Deploy with Render Blueprint (Recommended)

1. Click the "Deploy to Render" button below:

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/nathanstrauss13/ai-discoverability-analyzer)

2. Fill in the required environment variable:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key

3. Click "Create Web Service"

### Option 2: Manual Deployment

1. **Fork or connect your GitHub repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select the repository

2. **Configure the service**
   - Name: `ai-discoverability-analyzer`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Set environment variables**
   - Click "Environment" tab
   - Add the following:
     - `ANTHROPIC_API_KEY` = Your Anthropic API key
     - `PYTHON_VERSION` = 3.11.0

4. **Deploy**
   - Click "Create Web Service"
   - Wait for the build and deployment to complete

## Post-Deployment

Once deployed, your app will be available at:
```
https://ai-discoverability-analyzer.onrender.com
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude AI | Yes |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions (auto-generated) | No |
| `PYTHON_VERSION` | Python version (3.11.0) | No |

## Monitoring

- Check the "Logs" tab in Render dashboard for real-time logs
- Monitor the "Metrics" tab for performance data
- Set up health checks in the "Settings" tab

## Troubleshooting

1. **Build fails**: Check that all dependencies in `requirements.txt` are correct
2. **App crashes**: Check logs for error messages, ensure environment variables are set
3. **Slow performance**: Consider upgrading to a paid Render plan for better resources

## Custom Domain

To add a custom domain:
1. Go to Settings → Custom Domains
2. Add your domain
3. Update your DNS records as instructed

## Updates

To update your deployment:
1. Push changes to your GitHub repository
2. Render will automatically rebuild and redeploy

## Support

For issues specific to this app, please open an issue on GitHub.
For Render-specific issues, check their [documentation](https://render.com/docs).
