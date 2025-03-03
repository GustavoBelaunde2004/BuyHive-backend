from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.cart_routes import router as cart_router
from app.routers.item_routes import router as item_router
from app.routers.user_routes import router as user_router
from app.routers.extraction_routes import router as extraction_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(cart_router,tags=["Cart"])
app.include_router(item_router, tags=["Item"])
app.include_router(user_router, tags=["User"])
app.include_router(extraction_router, tags=["Extraction Processing"])
