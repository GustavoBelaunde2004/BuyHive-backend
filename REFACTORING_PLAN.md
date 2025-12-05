# BuyHive Backend - Production Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring plan to transform BuyHive's backend from a development prototype into a production-ready, secure, and scalable application. The refactoring is organized into 4 phases, prioritized by criticality and deployability.

**Target Timeline:** 6-10 days of focused development  
**Target Budget:** Free tier + minimal costs (~$5-10/month)  
**Deployment Target:** AWS (ECS Fargate/App Runner) with Docker

---

## Quick Context

**Project:** BuyHive Backend - Chrome extension shopping cart aggregator  
**Purpose:** Universal shopping cart that aggregates products from any e-commerce site using AI

**Key Features:**
- AI-powered product extraction from e-commerce pages (using Groq/OpenAI)
- Image verification using CLIP model (verifies scraped images match product names)
- URL classification using BERT model (detects if page is a product page)
- Multi-cart system (users can organize items across multiple carts)
- Email sharing functionality

**Tech Stack:**
- **Backend:** FastAPI (Python)
- **Database:** MongoDB Atlas
- **ML Models:** CLIP (image verification), BERT (URL classification)
- **LLM:** Groq (primary), OpenAI (fallback)
- **Email:** AWS SES (migrating from Gmail SMTP)
- **Deployment:** AWS ECS Fargate/App Runner with Docker
- **Monitoring:** Sentry + AWS CloudWatch

**Current Status:** Pre-production prototype - needs security hardening, authentication, and deployment setup

**Architecture Decisions:**
- Backend OAuth (Google) with JWT tokens (access + refresh)
- ML models run on CPU (same server) with lazy loading and caching
- Items can be shared across multiple carts (same item_id in different carts)
- On-demand scraping for now, background processing architecture designed for future

---

## Progress Tracking

### Phase 1: Critical Security & Foundation
- [ ] 1.1 Authentication System
- [ ] 1.2 CORS & Security Headers
- [ ] 1.3 Input Validation & Sanitization
- [ ] 1.4 Environment Configuration
- [ ] 1.5 Fix Hardcoded Paths

### Phase 2: Code Quality & Best Practices
- [ ] 2.1 Logging System
- [ ] 2.2 Error Handling Standardization
- [ ] 2.3 Update Deprecated APIs
- [ ] 2.4 Code Cleanup
- [ ] 2.5 Type Hints & Documentation

### Phase 3: Production Readiness
- [ ] 3.1 ML Model Optimization
- [ ] 3.2 Async HTTP Calls
- [ ] 3.3 Database Transactions
- [ ] 3.4 Rate Limiting
- [ ] 3.5 Health Checks & Monitoring
- [ ] 3.6 Email Service Migration

### Phase 4: Deployment & Infrastructure
- [ ] 4.1 Docker Setup
- [ ] 4.2 Environment Configuration
- [ ] 4.3 AWS Infrastructure Setup
- [ ] 4.4 CI/CD Pipeline
- [ ] 4.5 Documentation

**Last Updated:** [Update this date when making progress]  
**Current Phase:** Not Started  
**Overall Progress:** 0% (0/20 major tasks completed)

---

## Current State Analysis

### Strengths ✅
- Clean FastAPI structure with proper async/await usage
- Good use of Pydantic models for validation
- MongoDB with Motor (async driver)
- Clear separation of routers
- Functional core features (cart management, item extraction, ML verification)

### Critical Issues ⚠️
1. **Security:** No authentication, CORS allows all origins, no input validation
2. **Code Quality:** Deprecated APIs, inconsistent error handling, no logging
3. **Production Readiness:** Hardcoded paths, no monitoring, ML models loaded eagerly
4. **Deployment:** No Docker setup, no environment management, no CI/CD

---

## Architecture Decisions

### Authentication & Authorization
- **OAuth Provider:** Google OAuth 2.0 (extensible for more providers)
- **Token Strategy:** JWT with access tokens (15min) + refresh tokens (7 days)
- **Password Reset:** Email-based reset links via AWS SES
- **Implementation:** FastAPI OAuth2 with python-jose for JWT

### ML Models Strategy
- **CLIP Model:** CPU-based, lazy-loaded, cached results
- **BERT Model:** CPU-based, lazy-loaded, cached results
- **Target Latency:** <2 seconds for image verification
- **Caching:** Redis (free tier) or in-memory for MVP

### LLM Strategy
- **Phase 1:** Optimize Groq implementation with better prompts and retry logic
- **Phase 2:** Design architecture for self-hosted model (cloud-based)
- **Future:** Support multiple LLM providers (Groq, self-hosted, OpenAI fallback)

### Database
- **Keep:** MongoDB Atlas (current structure works well)
- **Enhancements:** Add indexes, connection pooling, transaction support
- **Backups:** Enable Atlas automated backups (free tier includes daily)

### Email Service
- **Provider:** AWS SES (free tier: 62,000 emails/month)
- **Migration:** Replace yagmail with boto3 SES client

### Monitoring & Observability
- **Error Tracking:** Sentry (free tier: 5,000 events/month)
- **Metrics:** AWS CloudWatch (free tier: 10 custom metrics)
- **Uptime:** CloudWatch alarms + basic health checks
- **Logging:** Structured logging with Python logging module

### Deployment
- **Platform:** AWS ECS Fargate (serverless containers) or App Runner
- **Containerization:** Docker with multi-stage builds
- **Environment:** Separate configs for dev/staging/prod
- **CI/CD:** GitHub Actions (free) for automated deployments

---

## Phase 1: Critical Security & Foundation (2-3 days)

**Priority:** 🔴 CRITICAL - Must complete before any production deployment

### 1.1 Authentication System (1 day)

#### Tasks:
- [ ] Install dependencies: `python-jose[cryptography]`, `python-multipart`, `passlib[bcrypt]`
- [ ] Create `app/auth/` directory structure
- [ ] Implement Google OAuth 2.0 flow
- [ ] Create JWT token generation and validation
- [ ] Add password reset functionality
- [ ] Create authentication middleware/dependencies
- [ ] Update all routes to require authentication
- [ ] Add user model to database

#### Files to Create:
```
app/
  auth/
    __init__.py
    oauth.py          # Google OAuth flow
    jwt_handler.py    # JWT creation/validation
    dependencies.py   # FastAPI dependencies for auth
    password_reset.py # Password reset logic
  models/
    user.py          # User model
```

#### Key Implementation Points:
- Use `python-jose` for JWT handling
- Store refresh tokens in database with expiration
- Hash passwords with bcrypt (for future email/password auth)
- Add `get_current_user` dependency for protected routes

### 1.2 CORS & Security Headers (30 min)

#### Tasks:
- [ ] Restrict CORS to specific origins (environment variable)
- [ ] Add security headers middleware
- [ ] Configure allowed methods and headers properly

#### Code Changes:
```python
# main.py
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Replace "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 1.3 Input Validation & Sanitization (2-3 hours)

#### Tasks:
- [ ] Add email validation to all email fields
- [ ] Add URL validation for product URLs
- [ ] Sanitize user inputs (prevent injection attacks)
- [ ] Add request size limits
- [ ] Validate file uploads (if any)

#### Updates Needed:
- Enhance Pydantic models with validators
- Add email regex validation
- Add URL validation
- Add input sanitization utilities

### 1.4 Environment Configuration (1 hour)

#### Tasks:
- [ ] Create `.env.example` file
- [ ] Move all config to environment variables
- [ ] Create `app/config/` for configuration management
- [ ] Add validation for required environment variables
- [ ] Fix hardcoded paths (especially BERT model path)

#### Files to Create:
```
app/
  config/
    __init__.py
    settings.py      # Pydantic Settings for config
```

#### Environment Variables Needed:
```env
# Database
MONGO_URL=

# OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=

# AWS
AWS_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Email (AWS SES)
SES_FROM_EMAIL=

# APIs
GROQ_API_KEY=
OPENAI_API_KEY=  # Keep for fallback

# ML Models
BERT_MODEL_PATH=  # Relative path or S3 URL

# Monitoring
SENTRY_DSN=

# App
ENVIRONMENT=development
```

### 1.5 Fix Hardcoded Paths (30 min)

#### Tasks:
- [ ] Update `bert_verifier.py` to use environment variable or relative path
- [ ] Make model paths configurable
- [ ] Add model download script if needed

---

## Phase 2: Code Quality & Best Practices (1-2 days)

**Priority:** 🟡 HIGH - Improves maintainability and reliability

### 2.1 Logging System (2-3 hours)

#### Tasks:
- [ ] Replace all `print()` statements with proper logging
- [ ] Configure structured logging (JSON format for production)
- [ ] Add log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Add request ID tracking
- [ ] Configure log rotation

#### Implementation:
```python
# app/utils/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(environment: str = "development"):
    logger = logging.getLogger("buyhive")
    handler = logging.StreamHandler(sys.stdout)
    
    if environment == "production":
        formatter = jsonlogger.JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

### 2.2 Error Handling Standardization (2-3 hours)

#### Tasks:
- [ ] Create custom exception classes
- [ ] Add global exception handler
- [ ] Standardize error response format
- [ ] Add proper HTTP status codes
- [ ] Log all errors with context

#### Files to Create:
```
app/
  exceptions/
    __init__.py
    custom_exceptions.py
    handlers.py      # Global exception handlers
```

### 2.3 Update Deprecated APIs (1 hour)

#### Tasks:
- [ ] Update OpenAI client to new API (v1.x)
- [ ] Replace `openai.ChatCompletion.create` with `OpenAI()` client
- [ ] Update Groq client if needed
- [ ] Test all AI integrations

#### Code Changes:
```python
# app/services/openai_parser.py
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def parse_inner_text_with_openai(input_text: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0,
    )
    result = response.choices[0].message.content
    # ... rest of the code
```

### 2.4 Code Cleanup (30 min)

#### Tasks:
- [ ] Remove duplicate `Item` class in `base.py`
- [ ] Remove unused imports
- [ ] Remove commented code (or convert to TODOs)
- [ ] Update deprecated Pydantic methods (`.dict()` → `.model_dump()`)

### 2.5 Type Hints & Documentation (2-3 hours)

#### Tasks:
- [ ] Add type hints to all functions
- [ ] Add docstrings to all public functions
- [ ] Add API documentation improvements
- [ ] Update README with new setup instructions

---

## Phase 3: Production Readiness (2-3 days)

**Priority:** 🟡 HIGH - Required for stable production deployment

### 3.1 ML Model Optimization (2-3 hours)

#### Tasks:
- [ ] Implement lazy loading for CLIP model
- [ ] Implement lazy loading for BERT model
- [ ] Add model caching mechanism
- [ ] Add result caching (Redis or in-memory)
- [ ] Add timeout handling for model inference
- [ ] Add model loading error handling

#### Implementation:
```python
# app/services/clip_verifier.py
_model = None
_tokenizer = None
_device = None

def _load_model():
    global _model, _tokenizer, _device
    if _model is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _model, _, preprocess_val = open_clip.create_model_and_transforms(
            'ViT-B-32', pretrained='openai'
        )
        _model.to(_device)
        _tokenizer = open_clip.get_tokenizer('ViT-B-32')
    return _model, _tokenizer, _device

def verify_image_with_clip(image_url: str, product_name: str) -> bool:
    model, tokenizer, device = _load_model()
    # ... rest of implementation
```

### 3.2 Async HTTP Calls (1-2 hours)

#### Tasks:
- [ ] Replace `requests` with `httpx` for async HTTP
- [ ] Update CLIP verifier to use async image fetching
- [ ] Add connection pooling
- [ ] Add timeout configuration

#### Code Changes:
```python
# app/services/clip_verifier.py
import httpx

async def verify_image_with_clip(image_url: str, product_name: str) -> bool:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        # ... rest of implementation
```

### 3.3 Database Transactions (3-4 hours)

#### Tasks:
- [ ] Add transaction support for multi-step operations
- [ ] Wrap cart/item operations in transactions
- [ ] Add retry logic for failed transactions
- [ ] Add database connection pooling configuration

### 3.4 Rate Limiting (2-3 hours)

#### Tasks:
- [ ] Install `slowapi` or implement custom rate limiter
- [ ] Add rate limits per user/IP
- [ ] Configure different limits for different endpoints
- [ ] Add rate limit headers to responses

#### Implementation:
```python
# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In routes
@router.post("/extract")
@limiter.limit("10/minute")
async def extract_cart_info(...):
    ...
```

### 3.5 Health Checks & Monitoring (1 hour)

#### Tasks:
- [ ] Enhance `/health` endpoint with detailed checks
- [ ] Add database connectivity check
- [ ] Add ML model availability check
- [ ] Add external API connectivity checks
- [ ] Set up Sentry error tracking
- [ ] Configure CloudWatch metrics

#### Enhanced Health Check:
```python
@app.get("/health")
async def health():
    checks = {
        "status": "healthy",
        "database": await check_database(),
        "ml_models": check_ml_models(),
        "timestamp": datetime.utcnow().isoformat()
    }
    status_code = 200 if all(v == "ok" for k, v in checks.items() if k != "status" and k != "timestamp") else 503
    return JSONResponse(content=checks, status_code=status_code)
```

### 3.6 Email Service Migration (1-2 hours)

#### Tasks:
- [ ] Install `boto3` for AWS SES
- [ ] Create email service module
- [ ] Migrate from yagmail to AWS SES
- [ ] Update email templates
- [ ] Add email sending error handling
- [ ] Test email delivery

#### Files to Create:
```
app/
  services/
    email_service.py  # AWS SES implementation
```

---

## Phase 4: Deployment & Infrastructure (1-2 days)

**Priority:** 🟢 MEDIUM - Required for actual deployment

### 4.1 Docker Setup (2-3 hours)

#### Tasks:
- [ ] Create `Dockerfile` with multi-stage build
- [ ] Create `.dockerignore`
- [ ] Optimize image size
- [ ] Add health check to Dockerfile
- [ ] Test Docker build locally

#### Dockerfile Structure:
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Environment Configuration (1-2 hours)

#### Tasks:
- [ ] Create environment-specific configs (dev/staging/prod)
- [ ] Set up AWS Parameter Store or Secrets Manager (optional)
- [ ] Create deployment scripts
- [ ] Document environment setup

### 4.3 AWS Infrastructure Setup (3-4 hours)

#### Tasks:
- [ ] Create AWS account (if not exists)
- [ ] Set up ECS cluster or App Runner service
- [ ] Configure ECR (Elastic Container Registry)
- [ ] Set up IAM roles and policies
- [ ] Configure VPC and security groups
- [ ] Set up CloudWatch log groups
- [ ] Configure AWS SES (verify domain/email)

#### AWS Resources Needed:
- ECS Cluster (Fargate) or App Runner service
- ECR repository for Docker images
- IAM role for ECS tasks
- Security groups
- CloudWatch log groups
- SES verified email/domain

### 4.4 CI/CD Pipeline (2-3 hours)

#### Tasks:
- [ ] Create GitHub Actions workflow
- [ ] Set up automated testing on PR
- [ ] Configure automated Docker build
- [ ] Set up automated deployment to staging
- [ ] Add manual approval for production deployment

#### GitHub Actions Workflow:
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Build and push Docker image
        run: |
          docker build -t buyhive-backend .
          # Push to ECR
      - name: Deploy to ECS
        run: |
          # Update ECS service
```

### 4.5 Documentation (2-3 hours)

#### Tasks:
- [ ] Update README with deployment instructions
- [ ] Create API documentation
- [ ] Document environment variables
- [ ] Create runbook for common operations
- [ ] Add architecture diagram

---

## Testing Strategy

### Critical Path Testing (Priority)

#### Authentication Tests:
- [ ] Google OAuth flow
- [ ] JWT token generation and validation
- [ ] Password reset flow
- [ ] Protected route access

#### Core Functionality Tests:
- [ ] Cart creation/retrieval/deletion
- [ ] Item addition/removal
- [ ] Item sharing across carts
- [ ] Product extraction
- [ ] Image verification
- [ ] URL classification

#### Integration Tests:
- [ ] Database operations
- [ ] External API calls (Groq, OpenAI)
- [ ] ML model inference
- [ ] Email sending

### Testing Tools:
- **Unit Tests:** pytest
- **API Tests:** pytest + httpx
- **Test Coverage:** pytest-cov (aim for 60%+ on critical paths)

---

## Cost Optimization

### AWS Free Tier Utilization:
- **ECS Fargate:** 20 GB-hours/month free (enough for low traffic)
- **ECR:** 500 MB storage free
- **CloudWatch:** 10 custom metrics, 5 GB log ingestion free
- **SES:** 62,000 emails/month free
- **Data Transfer:** 100 GB/month free

### Cost-Saving Tips:
1. Use Fargate Spot for non-critical workloads (70% savings)
2. Enable CloudWatch log retention (7 days for free tier)
3. Cache ML model results aggressively
4. Use connection pooling for database
5. Monitor and set up billing alerts

### Expected Monthly Costs:
- **Free Tier:** $0 (first 12 months for new accounts)
- **After Free Tier:** ~$5-10/month (low traffic)
- **With Growth:** Scale costs with usage

---

## Background Processing Architecture (Future)

### Design for Queue System:
- **Queue Service:** AWS SQS (free tier: 1 million requests/month)
- **Worker Service:** Separate ECS service for background jobs
- **Job Types:**
  - Pre-scraping product pages
  - Batch image verification
  - Email sending
  - Data cleanup

### Implementation Plan (Phase 5):
1. Set up SQS queues
2. Create worker service
3. Add job scheduling
4. Implement retry logic
5. Add job monitoring

---

## Migration Checklist

### Pre-Deployment:
- [ ] All Phase 1 tasks completed
- [ ] All Phase 2 tasks completed
- [ ] All Phase 3 tasks completed
- [ ] All Phase 4 tasks completed
- [ ] Critical tests passing
- [ ] Environment variables configured
- [ ] AWS resources created
- [ ] Docker image tested locally
- [ ] Database backups enabled

### Deployment:
- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Verify authentication works
- [ ] Test all critical endpoints
- [ ] Monitor logs and errors
- [ ] Deploy to production
- [ ] Set up monitoring alerts
- [ ] Document rollback procedure

### Post-Deployment:
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify email delivery
- [ ] Test user flows
- [ ] Gather user feedback

---

## Timeline Summary

| Phase | Duration | Priority | Can Deploy After? |
|-------|----------|----------|-------------------|
| Phase 1 | 2-3 days | 🔴 Critical | ✅ Yes (with caution) |
| Phase 2 | 1-2 days | 🟡 High | ✅ Yes (recommended) |
| Phase 3 | 2-3 days | 🟡 High | ✅ Yes (production-ready) |
| Phase 4 | 1-2 days | 🟢 Medium | ✅ Yes (fully deployed) |

**Total Estimated Time:** 6-10 days

---

## Next Steps

1. **Review this plan** and adjust priorities if needed
2. **Set up AWS account** and configure basic resources
3. **Start with Phase 1** - Critical Security & Foundation
4. **Test incrementally** after each phase
5. **Deploy to staging** after Phase 2
6. **Deploy to production** after Phase 3
7. **Monitor and iterate** based on real-world usage

---

## Notes

- This plan is designed to be **incremental** - you can deploy after each phase
- **Security is the top priority** - don't skip Phase 1
- **Testing is important** but can be done in parallel with development
- **Cost optimization** is built into the plan (free tier focus)
- **Future enhancements** (background processing, self-hosted LLM) are designed but not implemented

---

**Last Updated:** [Current Date]  
**Status:** Ready for Implementation  
**Owner:** Development Team

