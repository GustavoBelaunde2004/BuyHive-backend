"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock
from jose import JWTError


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
    
    def test_get_current_user_authenticated(self, authenticated_client):
        """Test getting current user info when authenticated."""
        response = authenticated_client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert data["email"] == "test@buyhive.com"
    
    def test_get_current_user_unauthenticated(self, unauthenticated_client):
        """Test that /auth/me requires authentication."""
        response = unauthenticated_client.get("/auth/me")
        # HTTPBearer returns 403 by default when no token is provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_current_user_invalid_token(self, unauthenticated_client):
        """Test that invalid tokens are rejected."""
        # Mock verify_auth0_token to raise JWTError for invalid tokens
        # This prevents the test from trying to connect to Auth0's JWKS endpoint
        # Use AsyncMock since verify_auth0_token is an async function
        async def raise_jwt_error(*args, **kwargs):
            raise JWTError("Invalid token")
        
        mock_verify = AsyncMock(side_effect=raise_jwt_error)
        with patch("app.core.dependencies.verify_auth0_token", new=mock_verify):
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

