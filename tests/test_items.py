"""
Tests for item management endpoints.
"""
import pytest
from fastapi import status


class TestItemEndpoints:
    """Test suite for item management endpoints."""
    
    @pytest.fixture
    def test_cart(self, authenticated_client, sample_cart_data):
        """Create a test cart and return its ID."""
        response = authenticated_client.post("/carts", json=sample_cart_data)
        assert response.status_code == status.HTTP_200_OK
        cart_id = response.json()["cart_id"]
        yield cart_id
        # Cleanup
        authenticated_client.delete(f"/carts/{cart_id}")
    
    def test_get_cart_items_empty(self, authenticated_client, test_cart):
        """Test getting items from an empty cart."""
        response = authenticated_client.get(f"/carts/{test_cart}/items")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 0
    
    def test_add_item_to_cart(self, authenticated_client, test_cart, sample_item_data):
        """Test adding an item to a cart."""
        response = authenticated_client.post(
            f"/carts/{test_cart}/items",
            json=sample_item_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "item_id" in data
        assert "message" in data
        
        # Verify item was added
        get_response = authenticated_client.get(f"/carts/{test_cart}/items")
        items = get_response.json()["items"]
        assert len(items) > 0
        assert any(item.get("name") == sample_item_data["name"] for item in items)
    
    def test_add_item_invalid_data(self, authenticated_client, test_cart):
        """Test adding item with invalid data."""
        # Missing required fields
        response = authenticated_client.post(
            f"/carts/{test_cart}/items",
            json={"name": "Test"}  # Missing price
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty name
        response = authenticated_client.post(
            f"/carts/{test_cart}/items",
            json={"name": "", "price": "99.99"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_item_unauthenticated(self, unauthenticated_client, sample_item_data):
        """Test that adding items requires authentication."""
        response = unauthenticated_client.post(
            "/carts/test_cart_id/items",
            json=sample_item_data
        )
        # HTTPBearer can return either 401 or 403 for missing/invalid tokens
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_get_items_unauthenticated(self, unauthenticated_client):
        """Test that getting items requires authentication."""
        response = unauthenticated_client.get("/carts/test_cart_id/items")
        # HTTPBearer can return either 401 or 403 for missing/invalid tokens
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_add_and_remove_item(self, authenticated_client, test_cart, sample_item_data):
        """Test adding and then removing an item."""
        # Add item
        add_response = authenticated_client.post(
            f"/carts/{test_cart}/items",
            json=sample_item_data
        )
        assert add_response.status_code == status.HTTP_200_OK
        item_id = add_response.json()["item_id"]
        
        # Verify item exists
        get_response = authenticated_client.get(f"/carts/{test_cart}/items")
        items = get_response.json()["items"]
        assert len(items) > 0
        
        # Remove item
        delete_response = authenticated_client.delete(f"/carts/{test_cart}/items/{item_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify item was removed
        get_response = authenticated_client.get(f"/carts/{test_cart}/items")
        items = get_response.json()["items"]
        assert not any(item.get("item_id") == item_id for item in items)
    
    def test_edit_item_note(self, authenticated_client, test_cart, sample_item_data):
        """Test editing an item's note."""
        # Add item first
        add_response = authenticated_client.post(
            f"/carts/{test_cart}/items",
            json=sample_item_data
        )
        item_id = add_response.json()["item_id"]
        
        # Edit note
        new_note = "Updated note"
        edit_response = authenticated_client.put(
            f"/carts/items/{item_id}/edit-note",
            json={"new_note": new_note}
        )
        assert edit_response.status_code == status.HTTP_200_OK
        
        # Verify note was updated
        get_response = authenticated_client.get(f"/carts/{test_cart}/items")
        items = get_response.json()["items"]
        item = next((i for i in items if i.get("item_id") == item_id), None)
        assert item is not None
        assert item.get("notes") == new_note

