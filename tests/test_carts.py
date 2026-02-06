"""
Tests for cart management endpoints.
"""
import pytest
from fastapi import status


class TestCartEndpoints:
    """Test suite for cart management endpoints."""
    
    def test_get_carts_authenticated(self, authenticated_client):
        """Test getting all carts when authenticated."""
        response = authenticated_client.get("/carts")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "carts" in data
        assert isinstance(data["carts"], list)
    
    def test_get_carts_unauthenticated(self, unauthenticated_client):
        """Test that getting carts requires authentication."""
        response = unauthenticated_client.get("/carts")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_create_cart_success(self, authenticated_client, sample_cart_data):
        """Test creating a new cart."""
        response = authenticated_client.post("/carts", json=sample_cart_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cart_id" in data
        assert "cart_name" in data
        assert "item_count" in data
        assert "created_at" in data
        assert "item_ids" in data
        # Verify cart was created by fetching it
        assert data["cart_name"] == sample_cart_data["cart_name"]
        
        # Store cart_id for cleanup
        cart_id = data["cart_id"]
        
        # Verify cart was created by fetching it
        get_response = authenticated_client.get("/carts")
        assert get_response.status_code == status.HTTP_200_OK
        carts = get_response.json()["carts"]
        assert any(cart.get("cart_id") == cart_id for cart in carts)
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id}")
    
    def test_create_cart_invalid_data(self, authenticated_client):
        """Test creating cart with invalid data."""
        # Missing cart_name
        response = authenticated_client.post("/carts", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty cart_name
        response = authenticated_client.post("/carts", json={"cart_name": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_cart_unauthenticated(self, unauthenticated_client, sample_cart_data):
        """Test that creating cart requires authentication."""
        response = unauthenticated_client.post("/carts", json=sample_cart_data)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_edit_cart_name(self, authenticated_client, sample_cart_data):
        """Test editing cart name."""
        # Create a cart first
        create_response = authenticated_client.post("/carts", json=sample_cart_data)
        assert create_response.status_code == status.HTTP_200_OK
        cart_id = create_response.json()["cart_id"]
        
        # Edit the cart name
        new_name = "Updated Cart Name"
        edit_response = authenticated_client.put(
            f"/carts/{cart_id}/edit-name",
            json={"new_name": new_name}
        )
        assert edit_response.status_code == status.HTTP_200_OK
        
        # Verify the name was updated
        get_response = authenticated_client.get("/carts")
        carts = get_response.json()["carts"]
        updated_cart = next((c for c in carts if c.get("cart_id") == cart_id), None)
        assert updated_cart is not None
        assert updated_cart.get("cart_name") == new_name
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id}")
    
    def test_delete_cart(self, authenticated_client, sample_cart_data):
        """Test deleting a cart."""
        # Create a cart first
        create_response = authenticated_client.post("/carts", json=sample_cart_data)
        assert create_response.status_code == status.HTTP_200_OK
        cart_id = create_response.json()["cart_id"]
        
        # Delete the cart
        delete_response = authenticated_client.delete(f"/carts/{cart_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify cart was deleted
        get_response = authenticated_client.get("/carts")
        carts = get_response.json()["carts"]
        assert not any(cart.get("cart_id") == cart_id for cart in carts)
    
    def test_delete_nonexistent_cart(self, authenticated_client):
        """Test deleting a cart that doesn't exist."""
        response = authenticated_client.delete("/carts/nonexistent_cart_id")
        # Should either return 404 or 200 with error message
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_duplicate_cart_name(self, authenticated_client, sample_cart_data):
        """Test creating multiple carts with the same name."""
        # Create first cart
        response1 = authenticated_client.post("/carts", json=sample_cart_data)
        assert response1.status_code == status.HTTP_200_OK
        cart_id1 = response1.json()["cart_id"]
        
        # Create second cart with same name
        response2 = authenticated_client.post("/carts", json=sample_cart_data)
        assert response2.status_code == status.HTTP_200_OK
        response2_data = response2.json()
        assert "cart_id" in response2_data, f"Response should contain cart_id: {response2_data}"
        cart_id2 = response2_data["cart_id"]
        
        # Both should exist (duplicate names are allowed)
        get_response = authenticated_client.get("/carts")
        carts = get_response.json()["carts"]
        assert len([c for c in carts if c.get("cart_id") in [cart_id1, cart_id2]]) == 2
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id1}")
        authenticated_client.delete(f"/carts/{cart_id2}")
    
    def test_very_long_cart_name(self, authenticated_client):
        """Test creating cart with very long name."""
        long_name = "A" * 1000  # Very long name
        response = authenticated_client.post("/carts", json={"cart_name": long_name})
        # Should either succeed (if no limit) or fail validation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_200_OK:
            cart_id = response.json()["cart_id"]
            authenticated_client.delete(f"/carts/{cart_id}")

