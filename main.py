from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from app.routers.auth_routes import router as auth_router
from app.routers.cart_routes import router as cart_router
from app.routers.item_routes import router as item_router
from app.routers.user_routes import router as user_router
from app.routers.extraction_routes import router as extraction_router
from app.config.settings import settings
from app.services.clip_verifier import check_clip_model_status
from app.services.bert_verifier import MODEL_AVAILABLE
from app.services.vision_verifier import check_openai_vision_availability
from app.functions.database import client
from datetime import datetime
import httpx

app = FastAPI()

# Rate limiting setup
if settings.RATE_LIMIT_ENABLED:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from app.utils.rate_limiter import limiter
    
    if limiter:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to 10MB."""
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        max_size = 10 * 1024 * 1024  # 10MB
        if len(body) > max_size:
            return Response(
                content="Request body too large. Maximum size is 10MB.",
                status_code=413
            )
        # Recreate request with body for downstream handlers
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
    return await call_next(request)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # Restricted to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

async def check_database_connection() -> dict:
    """Check if database connection is healthy."""
    try:
        # Ping the database
        await client.admin.command('ping')
        return {"status": "ok", "message": "Database connection healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def check_openai_connectivity() -> dict:
    """Check if OpenAI API is reachable."""
    if not settings.OPENAI_API_KEY:
        return {"status": "unavailable", "message": "OpenAI API key not configured"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as http_client:
            # Simple connectivity check - OpenAI API doesn't have a ping endpoint
            # So we just check if the key is configured
            return {"status": "ok", "message": "OpenAI API key configured"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_bert_model_status() -> dict:
    """Check if BERT model is available."""
    if MODEL_AVAILABLE:
        return {"status": "ok", "message": "BERT model available"}
    else:
        return {"status": "unavailable", "message": "BERT model not configured or not found"}

@app.get("/health")
async def health():
    """Enhanced health check endpoint with detailed service status."""
    checks = {
        "status": "healthy",
        "database": await check_database_connection(),
        "clip_model": check_clip_model_status(),
        "bert_model": check_bert_model_status(),
        "openai_api": await check_openai_connectivity(),
        "openai_vision": await check_openai_vision_availability(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Determine overall status
    critical_checks = ["database", "clip_model"]
    all_critical_ok = all(
        checks[key].get("status") == "ok" 
        for key in critical_checks 
        if key in checks
    )
    
    status_code = 200 if all_critical_ok else 503
    if not all_critical_ok:
        checks["status"] = "degraded"
    
    return JSONResponse(content=checks, status_code=status_code)

@app.get("/health/ready")
async def readiness():
    """Readiness probe - checks if service is ready to accept traffic."""
    checks = {
        "status": "ready",
        "database": await check_database_connection(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Readiness requires database to be available
    is_ready = checks["database"].get("status") == "ok"
    status_code = 200 if is_ready else 503
    
    if not is_ready:
        checks["status"] = "not_ready"
    
    return JSONResponse(content=checks, status_code=status_code)

@app.get("/health/live")
def liveness():
    """Liveness probe - checks if service is alive."""
    return JSONResponse(
        content={
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=200
    )


# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(cart_router, prefix="/carts", tags=["Cart"])
app.include_router(item_router, prefix="/carts", tags=["Item"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(extraction_router, prefix="/extract", tags=["Extraction Processing"])
