# BuyHive Backend - Deployment Guide

This guide covers deploying BuyHive backend to Railway using Docker.

## Prerequisites

- Docker installed and running
- GitHub repository with Actions enabled
- MongoDB Atlas cluster (or self-hosted MongoDB)
- Auth0 account configured
- API keys: Groq, OpenAI

## Quick Start

### 1. Local Testing with Docker

```bash
# Build the image
docker build -t buyhive-backend:latest .

# Run locally
docker run -p 8000:8000 --env-file .env buyhive-backend:latest

# Test health endpoint
curl http://localhost:8000/health
```

### 2. Using Docker Compose (with MongoDB)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Railway Deployment

### 1. Create a Railway project

1. Railway → **New Project** → **Deploy from GitHub Repo**
2. Select this repository
3. Railway will build from the `Dockerfile` and start the service

### 2. Configure environment variables (Railway → Project → Variables)

Set the minimum required variables:

- `ENVIRONMENT=production`
- `MONGO_URL`
- `AUTH0_DOMAIN`
- `AUTH0_AUDIENCE`
- `ALLOWED_ORIGINS` (comma-separated)
- `GROQ_API_KEY`
- `OPENAI_API_KEY`
- `PORT=8000`

Optional:
- `BERT_MODEL_PATH` (only if you’re enabling URL classification in production)

Email (AWS SES) is supported but optional for first deploy:
- If you do **not** set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_FROM_EMAIL`, email sending will be disabled, but the backend will still run.

## Environment Configuration

### Development

1. Copy `.env.example` to `.env`
2. Fill in all required variables
3. Run locally: `uvicorn main:app --reload`

### Production

1. Copy `.env.example` to `.env.production`
2. Fill in production values
3. Set `ENVIRONMENT=production`
4. Deploy via CI/CD or manually

### Required Environment Variables

Minimum required:

- `MONGO_URL` - MongoDB connection string
- `AUTH0_DOMAIN` - Auth0 tenant domain
- `AUTH0_AUDIENCE` - Auth0 API identifier
- `ALLOWED_ORIGINS` - Comma-separated allowed origins
- `GROQ_API_KEY` - Groq API key
- `OPENAI_API_KEY` - OpenAI API key
- `ENVIRONMENT` - Set to `production` in Railway
- `PORT` - Set to `8000`

## CI/CD (tests only)

GitHub Actions runs tests on:
- pull requests to `main` / `develop`
- pushes to `main`

Railway handles the deployment from GitHub.

## Logs

Use Railway logs:
- Railway → Project → Deployments → View logs

## Health checks

- `GET /health`
- `GET /health/ready`
- `GET /health/live`

## Support

For issues or questions:
- Check [RUNBOOK.md](./RUNBOOK.md) for common operations
- Review [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API details
- Open an issue on GitHub






