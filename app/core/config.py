from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Database
    MONGO_URL: str
    
    # Auth0
    AUTH0_DOMAIN: str = ""
    AUTH0_AUDIENCE: str = ""  # API Identifier from Auth0
    AUTH0_ALGORITHMS: str = "RS256"  # Auth0 uses RS256
    
    # JWT (for internal use if needed)
    JWT_SECRET_KEY: str = ""  # Not needed for Auth0, but kept for compatibility
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Default expiration
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Default expiration
    
    # CORS
    ALLOWED_ORIGINS: str = ""  # Comma-separated list
    
    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # Email (AWS SES)
    SES_FROM_EMAIL: str = ""
    
    # Legacy Email (Gmail - will be replaced by SES)
    GMAIL_USER: str = ""
    GMAIL_PASSWORD: str = ""
    
    # APIs
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_SEARCH_API: str = ""
    CSE_ID: str = ""
    GOOGLE_SHEETS_SCRIPT_URL: str = ""
    
    # ML Models
    BERT_MODEL_PATH: str = ""
    
    # CLIP Configuration
    CLIP_THRESHOLD: float = 0.28  # Similarity threshold for image verification
    ENABLE_VISION_FALLBACK: bool = True  # Use OpenAI Vision as fallback when CLIP fails
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        # Load from .env file (default)
        # For environment-specific configs, use .env.production, .env.staging, etc.
        # and set ENVIRONMENT variable, or pass env_file when instantiating
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables (like CLIENT_ID, CLIENT_SECRET)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS to list."""
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    def validate_production(self):
        """Validate required settings for production environment."""
        if self.ENVIRONMENT == "production":
            required_vars = [
                "MONGO_URL",
                "AUTH0_DOMAIN",
                "AUTH0_AUDIENCE",
                "ALLOWED_ORIGINS",
            ]
            missing = [var for var in required_vars if not getattr(self, var, None)]
            if missing:
                raise ValueError(
                    f"Missing required environment variables for production: {', '.join(missing)}"
                )


# Create settings instance
settings = Settings()

# Validate production settings
if settings.ENVIRONMENT == "production":
    settings.validate_production()

