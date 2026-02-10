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
                        assert "refresh_token" in data
                        assert "token_type" in data
                        assert data["token_type"] == "bearer"
                        assert len(data["access_token"]) > 0
                        assert len(data["refresh_token"]) > 0
    
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
    
    def test_refresh_token_valid(self, unauthenticated_client, test_refresh_token, mock_user_in_db, ensure_jwt_secret_key):
        """Test refresh endpoint with valid refresh token."""
        import app.routers.auth_routes as auth_routes_module
        import app.core.security as security_module
        import app.core.database as db_module
        from app.core.config import settings
        from tests.conftest import TEST_JWT_SECRET_KEY
        
        # Ensure JWT_SECRET_KEY is set
        settings.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        
        # Mock verify_token to work with our test refresh token
        def mock_verify_token(token: str, token_type: str = "access"):
            from jose import jwt
            
            if token == test_refresh_token and token_type == "refresh":
                payload = jwt.decode(
                    token,
                    TEST_JWT_SECRET_KEY,
                    algorithms=["HS256"]
                )
                if payload.get("type") != "refresh":
                    raise JWTError("Invalid token type")
                return payload
            raise JWTError("Invalid token")
        
        # Mock users_collection.find_one to return user data
        async def mock_find_one(query: dict):
            if query.get("user_id") == TEST_AUTH0_ID:
                return mock_user_in_db
            return None
        
        users_collection_mock = AsyncMock()
        users_collection_mock.find_one = AsyncMock(side_effect=mock_find_one)
        
        with patch.object(auth_routes_module, "verify_token", new=mock_verify_token):
            with patch.object(security_module, "verify_token", new=mock_verify_token):
                with patch.object(auth_routes_module, "users_collection", users_collection_mock):
                    with patch.object(db_module, "users_collection", users_collection_mock):
                        response = unauthenticated_client.post(
                            "/auth/refresh",
                            headers={"Authorization": f"Bearer {test_refresh_token}"}
                        )
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert "access_token" in data
                        assert "refresh_token" in data
                        assert "token_type" in data
                        assert data["token_type"] == "bearer"
                        assert len(data["access_token"]) > 0
                        assert len(data["refresh_token"]) > 0
    
    def test_refresh_token_invalid(self, unauthenticated_client):
        """Test refresh endpoint with invalid refresh token."""
        import app.routers.auth_routes as auth_routes_module
        import app.core.security as security_module
        
        def raise_jwt_error(*args, **kwargs):
            raise JWTError("Invalid token")
        
        mock_verify = MagicMock(side_effect=raise_jwt_error)
        with patch.object(auth_routes_module, "verify_token", new=mock_verify):
            with patch.object(security_module, "verify_token", new=mock_verify):
                response = unauthenticated_client.post(
                    "/auth/refresh",
                    headers={"Authorization": "Bearer invalid_refresh_token"}
                )
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_expired(self, unauthenticated_client, ensure_jwt_secret_key):
        """Test refresh endpoint with expired refresh token."""
        import app.routers.auth_routes as auth_routes_module
        import app.core.security as security_module
        from jose import jwt
        from datetime import datetime, timedelta
        from tests.conftest import TEST_JWT_SECRET_KEY
        
        # Create an expired refresh token
        expired_jwt_data = {
            "sub": TEST_AUTH0_ID,
            "email": TEST_USER_EMAIL,
            "name": TEST_USER_NAME,
            "auth0_id": TEST_AUTH0_ID,
            "type": "refresh",
            "exp": int((datetime.utcnow() - timedelta(days=1)).timestamp()),  # Expired yesterday
        }
        expired_token = jwt.encode(
            expired_jwt_data,
            TEST_JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        def mock_verify_token(token: str, token_type: str = "access"):
            # This will raise ExpiredSignatureError when decoding
            from jose import ExpiredSignatureError
            try:
                payload = jwt.decode(
                    token,
                    TEST_JWT_SECRET_KEY,
                    algorithms=["HS256"]
                )
                if payload.get("type") != token_type:
                    raise JWTError("Invalid token type")
                return payload
            except ExpiredSignatureError:
                raise JWTError("Token has expired")
        
        with patch.object(auth_routes_module, "verify_token", new=mock_verify_token):
            with patch.object(security_module, "verify_token", new=mock_verify_token):
                response = unauthenticated_client.post(
                    "/auth/refresh",
                    headers={"Authorization": f"Bearer {expired_token}"}
                )
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_with_access_token(self, unauthenticated_client, test_internal_jwt):
        """Test refresh endpoint with access token (should fail - wrong token type)."""
        import app.routers.auth_routes as auth_routes_module
        import app.core.security as security_module
        from jose import jwt
        from tests.conftest import TEST_JWT_SECRET_KEY
        
        def mock_verify_token(token: str, token_type: str = "access"):
            if token == test_internal_jwt:
                payload = jwt.decode(
                    token,
                    TEST_JWT_SECRET_KEY,
                    algorithms=["HS256"]
                )
                if payload.get("type") != token_type:
                    raise JWTError(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return payload
            raise JWTError("Invalid token")
        
        with patch.object(auth_routes_module, "verify_token", new=mock_verify_token):
            with patch.object(security_module, "verify_token", new=mock_verify_token):
                response = unauthenticated_client.post(
                    "/auth/refresh",
                    headers={"Authorization": f"Bearer {test_internal_jwt}"}
                )
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token_missing(self, unauthenticated_client):
        """Test refresh endpoint with missing token."""
        response = unauthenticated_client.post("/auth/refresh")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

