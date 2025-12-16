# BuyHive Backend - Refactoring Plan (Current: Railway Deploy)

This is the updated refactoring plan after switching deployment from AWS ECS/ECR to Railway. We keep **AWS SES only** as an optional email provider.

## Goals

- Production-ready FastAPI backend
- Safe configuration via environment variables
- Reliable CI tests (GitHub Actions)
- Simple deployment via Railway (Docker)
- Optional email via AWS SES (later)

## Phase 1: Security & Foundation

- Authentication via Auth0 JWT verification
- CORS restricted via `ALLOWED_ORIGINS`
- Request size limits + basic sanitization
- Centralized config via `app/config/settings.py`

## Phase 2: Code Quality & Observability (lightweight)

- Remove debug `print()` statements
- Standardize error responses and logging (optional follow-up)

## Phase 3: Production Readiness

- Lazy loading for CLIP and BERT
- Async HTTP (`httpx`)
- MongoDB connection pooling
- Rate limiting (`slowapi`)
- Health endpoints: `/health`, `/health/ready`, `/health/live`
- Email sending via SES module (optional, can be enabled later)

## Phase 4: Deployment & Infrastructure (Railway)

- Docker build via `Dockerfile`
- Deploy via Railway “Deploy from GitHub”
- Required Railway env vars:
  - `ENVIRONMENT=production`
  - `PORT=8000`
  - `MONGO_URL`
  - `AUTH0_DOMAIN`
  - `AUTH0_AUDIENCE`
  - `ALLOWED_ORIGINS`
  - `GROQ_API_KEY`
  - `OPENAI_API_KEY`
- Optional env vars:
  - `BERT_MODEL_PATH` (only if you enable URL classification in prod)
  - SES email: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_FROM_EMAIL`

## Next improvements (post-deploy)

- Extraction robustness (multi-layer extraction + HTML minimization)
- Structured logging (JSON logs) and better error taxonomy
- Background jobs/queue (only if needed)


