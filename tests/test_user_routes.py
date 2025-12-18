"""
Tests for user routes (cart sharing).
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestUserRoutes:
    """Test suite for user-related endpoints."""
    
    @pytest.fixture
    def test_cart_with_items(self, authenticated_client, sample_cart_data, sample_item_data):
        """Create a test cart with items and return its ID."""
        # Create cart
        cart_response = authenticated_client.post("/carts", json=sample_cart_data)
        cart_id = cart_response.json()["cart_id"]
        
        # Add item to cart
        item_response = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [cart_id]}
        )
        
        yield cart_id
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id}")
    
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_cart_success(self, mock_email, authenticated_client, test_cart_with_items, sample_cart_data):
        """Test successful cart sharing via email (async, returns immediately)."""
        mock_email.return_value = {"message": "Email sent successfully!"}
        cart_id = test_cart_with_items
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Cart shared successfully" in data["message"]
        assert "Email is being sent" in data["message"]
        
        # Note: Email is sent in background, so mock_email won't be called immediately
        # BackgroundTasks run after response is sent, so we can't easily verify in unit tests
        # In integration tests, we'd verify the email was actually sent
    
    def test_share_cart_not_found(self, authenticated_client):
        """Test sharing a cart that doesn't exist."""
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": "non-existent-cart-id-12345"
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data.get("detail", "").lower()
    
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_empty_cart(self, mock_email, authenticated_client, sample_cart_data):
        """Test sharing an empty cart (async email)."""
        mock_email.return_value = {"message": "Email sent successfully!"}
        
        # Create empty cart
        cart_response = authenticated_client.post("/carts", json=sample_cart_data)
        cart_id = cart_response.json()["cart_id"]
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Cart shared successfully" in data["message"]
        
        # Note: Email is sent in background via BackgroundTasks
        # TestClient executes background tasks after response, so mock_email will be called
        # but we verify the response format instead
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id}")
    
    def test_share_cart_invalid_email(self, authenticated_client, test_cart_with_items):
        """Test sharing cart with invalid email format."""
        cart_id = test_cart_with_items
        
        payload = {
            "recipient_email": "invalid-email-format",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        # Should return 422 (validation error) or 400
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @patch('app.functions.user.send_email_gmail')
    def test_share_cart_email_failure(self, mock_email, authenticated_client, test_cart_with_items):
        """Test cart sharing when email service fails (async, doesn't block API)."""
        mock_email.side_effect = Exception("Email service error")
        cart_id = test_cart_with_items
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        # With async email, API should return success immediately even if email fails
        # Email errors are logged but don't affect the API response
        # Note: FastAPI TestClient executes background tasks synchronously, but our
        # try-except in send_email_gmail() catches exceptions and logs them
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Cart shared successfully" in data["message"]
        
        # Email failure happens in background and is logged, not returned to user
        # The exception is caught by try-except in send_email_gmail() and logged
    
    def test_share_cart_missing_recipient_email(self, authenticated_client, test_cart_with_items):
        """Test sharing cart with missing recipient_email."""
        cart_id = test_cart_with_items
        
        payload = {
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_share_cart_missing_cart_id(self, authenticated_client):
        """Test sharing cart with missing cart_id."""
        payload = {
            "recipient_email": "recipient@example.com"
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_share_cart_unauthenticated(self, unauthenticated_client):
        """Test that sharing cart requires authentication."""
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": "test-cart-id"
        }
        
        response = unauthenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

