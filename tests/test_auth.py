"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""
    
    def test_health_check(self, unauthenticated_client):
        """Test that health endpoint is accessible without authentication."""
        response = unauthenticated_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"ok": True}
    
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

