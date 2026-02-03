"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from jose import JWTError
from tests.conftest import TEST_USER_EMAIL, TEST_USER_NAME, TEST_AUTH0_ID


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_health_check(self, unauthenticated_client):
        """Test that health endpoint is accessible without authentication."""
        response = unauthenticated_client.get("/health")
        # Health check may return 200 (healthy) or 503 (degraded) depending on service availability
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        data = response.json()
        # Check for new health check format with detailed status
        assert "status" in data
        assert "timestamp" in data
        # May have service checks (database, openai_api, etc.)
    
    def test_exchange_auth0_token_valid(self, unauthenticated_client, mock_verify_auth0_token, mock_get_or_create_user, ensure_jwt_secret_key):
        """Test exchange endpoint with valid Auth0 token."""
        import app.routers.auth_routes as auth_routes_module
        import app.core.security as security_module
        from app.core.config import settings
        from tests.conftest import TEST_JWT_SECRET_KEY
        
        # Ensure JWT_SECRET_KEY is set for create_access_token
        settings.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        
        # Patch where functions are USED (auth_routes module) AND where they're DEFINED (security module)
        with patch.object(auth_routes_module, "verify_auth0_token", new=mock_verify_auth0_token):
            with patch.object(auth_routes_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
                with patch.object(security_module, "verify_auth0_token", new=mock_verify_auth0_token):
                    with patch.object(security_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
                        response = unauthenticated_client.post(
                            "/auth/exchange",
                            headers={"Authorization": "Bearer valid_auth0_token"}
                        )
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert "access_token" in data
                        assert "token_type" in data
                        assert data["token_type"] == "bearer"
                        assert len(data["access_token"]) > 0
    
    def test_exchange_auth0_token_invalid(self, unauthenticated_client):
        """Test exchange endpoint with invalid Auth0 token."""
        import app.core.security as security_module
        
        async def raise_jwt_error(*args, **kwargs):
            raise JWTError("Invalid Auth0 token")
        
        mock_verify = AsyncMock(side_effect=raise_jwt_error)
        with patch.object(security_module, "verify_auth0_token", new=mock_verify):
            response = unauthenticated_client.post(
                "/auth/exchange",
                headers={"Authorization": "Bearer invalid_token"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_exchange_auth0_token_missing(self, unauthenticated_client):
        """Test exchange endpoint with missing token."""
        response = unauthenticated_client.post("/auth/exchange")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_current_user_authenticated(self, authenticated_client):
        """Test getting current user info when authenticated."""
        response = authenticated_client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert data["email"] == TEST_USER_EMAIL
    
    def test_get_current_user_unauthenticated(self, unauthenticated_client):
        """Test that /auth/me requires authentication."""
        response = unauthenticated_client.get("/auth/me")
        # HTTPBearer returns 403 by default when no token is provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_current_user_invalid_token(self, unauthenticated_client):
        """Test that invalid tokens are rejected."""
        # Mock verify_token to raise JWTError for invalid tokens
        def raise_jwt_error(*args, **kwargs):
            raise JWTError("Invalid token")
        
        mock_verify = MagicMock(side_effect=raise_jwt_error)
        with patch("app.core.dependencies.verify_token", new=mock_verify):
            response = unauthenticated_client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid_token"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_missing_token(self, unauthenticated_client):
        """Test that missing token is rejected."""
        response = unauthenticated_client.get("/auth/me")
        # HTTPBearer returns 403 by default when no token is provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_logout_authenticated(self, authenticated_client):
        """Test logout endpoint when authenticated."""
        response = authenticated_client.post("/auth/logout")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

