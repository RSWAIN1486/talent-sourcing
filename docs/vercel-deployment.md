# Vercel Deployment Guide

## Environment Variables Setup

To set up environment variables in Vercel:`

1. Go to your project dashboard in Vercel
2. Navigate to Settings > Environment Variables
3. Add the following environment variables:

### Required Environment Variables

```plaintext
# MongoDB settings
MONGODB_USERNAME=your-mongodb-username
MONGODB_PASSWORD=your-mongodb-password
MONGODB_CLUSTER=your-cluster.mongodb.net
MONGODB_URL=mongodb+srv://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@${MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=recruitment_ai

# JWT settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]

# File upload settings
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=["pdf","zip"]

# Application settings
PROJECT_NAME="Talent Sourcing API"
VERSION=0.1.0
API_V1_STR=/api/v1

# AI API settings
AI_API_KEY=your-ai-api-key-here
AI_BASE_URL=https://api.deepinfra.com/v1/openai
```

### Important Notes:

1. Make sure to update `BACKEND_CORS_ORIGINS` with your actual frontend domain after deployment
2. Never commit sensitive environment variables to version control
3. Use different environment variables for Development, Preview, and Production environments in Vercel
4. You can set environment variables through:
   - Vercel's web interface
   - Vercel CLI
   - Using the Vercel project settings

### Setting Environment Variables via Vercel CLI

If you prefer using the CLI:

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Login to Vercel
vercel login

# Add environment variables
vercel env add MONGODB_USERNAME
vercel env add MONGODB_PASSWORD
# ... and so on for each variable

# To pull environment variables locally (for development)
vercel env pull
```

## Deployment Steps

1. Push your code to GitHub
2. Import your repository in Vercel
3. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `backend`
   - Install Command: `pip install -r requirements.txt`
4. Set up environment variables as described above
5. Deploy your application

## Environment Variable Scopes

In Vercel, you can set different values for each environment:
- Production (main branch)
- Preview (pull requests)
- Development (local development)

To set environment-specific variables, use the dropdown in the Environment Variables section of your project settings. 