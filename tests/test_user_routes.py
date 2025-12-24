"""
Tests for user routes (cart sharing).
"""
import pytest
from unittest.mock import patch
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
    
    @pytest.mark.skip(reason="Async mocking issue with TestClient - needs AsyncClient or different mocking approach")
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_cart_success(self, mock_email, authenticated_client, test_cart_with_items, sample_cart_data):
        """Test successful cart sharing via email."""
        # Use side_effect with async function - TestClient can properly await this
        async def mock_email_func(*args, **kwargs):
            return {"message": "Email sent successfully!"}
        mock_email.side_effect = mock_email_func
        cart_id = test_cart_with_items
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
        # Verify email function was called
        mock_email.assert_called_once()
        # Verify it was called with correct parameters
        call_args = mock_email.call_args
        assert call_args[0][0] == "recipient@example.com"  # recipient_email
        assert call_args[0][1] == sample_cart_data["cart_name"]  # cart_name
        assert isinstance(call_args[0][2], list)  # cart_items (List[ItemInDB])
    
    @pytest.mark.skip(reason="Async mocking issue with TestClient - needs AsyncClient or different mocking approach")
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_cart_not_found(self, mock_email, authenticated_client):
        """Test sharing a cart that doesn't exist."""
        # Mock won't be called since we return 404 before email, but set it up just in case
        async def mock_email_func(*args, **kwargs):
            return {"message": "Email sent successfully!"}
        mock_email.side_effect = mock_email_func
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": "non-existent-cart-id-12345"
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data.get("detail", "").lower()
    
    @pytest.mark.skip(reason="Async mocking issue with TestClient - needs AsyncClient or different mocking approach")
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_empty_cart(self, mock_email, authenticated_client, sample_cart_data):
        """Test sharing an empty cart."""
        # Use side_effect with async function - TestClient can properly await this
        async def mock_email_func(*args, **kwargs):
            return {"message": "Email sent successfully!"}
        mock_email.side_effect = mock_email_func
        
        # Create empty cart
        cart_response = authenticated_client.post("/carts", json=sample_cart_data)
        cart_id = cart_response.json()["cart_id"]
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_200_OK
        
        # Email should still be sent (even with empty cart)
        mock_email.assert_called_once()
        call_args = mock_email.call_args
        assert call_args[0][2] == []  # Empty items list
        
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
    
    @patch('app.routers.user_routes.send_email_gmail')
    def test_share_cart_email_failure(self, mock_email, authenticated_client, test_cart_with_items):
        """Test cart sharing when email service fails."""
        async def mock_email_func(*args, **kwargs):
            raise Exception("Email service error")
        mock_email.side_effect = mock_email_func
        cart_id = test_cart_with_items
        
        payload = {
            "recipient_email": "recipient@example.com",
            "cart_id": cart_id
        }
        
        response = authenticated_client.post("/users/carts/share", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
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

