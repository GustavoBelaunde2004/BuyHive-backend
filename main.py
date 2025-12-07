from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.routers.auth_routes import router as auth_router
from app.routers.cart_routes import router as cart_router
from app.routers.item_routes import router as item_router
from app.routers.user_routes import router as user_router
from app.routers.extraction_routes import router as extraction_router
from app.config.settings import settings

app = FastAPI()

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

@app.get("/health")
def health():
    return {"ok": True}


# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(cart_router, prefix="/carts", tags=["Cart"])
app.include_router(item_router, prefix="/carts", tags=["Item"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(extraction_router, prefix="/extract", tags=["Extraction Processing"])
