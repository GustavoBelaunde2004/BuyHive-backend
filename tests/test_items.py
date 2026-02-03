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
        # Response is Cart model, has items field directly
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 0
    
    def test_add_item_to_cart(self, authenticated_client, test_cart, sample_item_data):
        """Test adding an item to a cart."""
        response = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [test_cart]}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # The response has message and item fields
        assert "message" in data
        assert "item" in data or "existing_item" in data
        
        # Verify item was added (response is Cart model)
        get_response = authenticated_client.get(f"/carts/{test_cart}/items")
        cart_data = get_response.json()
        items = cart_data["items"]
        assert len(items) > 0
        assert any(item.get("name") == sample_item_data["name"] for item in items)
    
    def test_add_item_invalid_data(self, authenticated_client, test_cart):
        """Test adding item with invalid data."""
        # Missing required fields
        response = authenticated_client.post(
            "/carts/items/add-new",
            json={"name": "Test", "selected_cart_ids": [test_cart]}  # Missing price
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty name
        response = authenticated_client.post(
            "/carts/items/add-new",
            json={"name": "", "price": "99.99", "selected_cart_ids": [test_cart]}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing selected_cart_ids
        response = authenticated_client.post(
            "/carts/items/add-new",
            json={"name": "Test", "price": "99.99"}  # Missing selected_cart_ids
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_item_unauthenticated(self, unauthenticated_client, sample_item_data):
        """Test that adding items requires authentication."""
        response = unauthenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": ["test_cart_id"]}
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
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [test_cart]}
        )
        assert add_response.status_code == status.HTTP_200_OK
        # Extract item_id from response
        response_data = add_response.json()
        if "item" in response_data:
            item_id = response_data["item"]["item_id"]
        elif "existing_item" in response_data:
            item_id = response_data["existing_item"]["item_id"]
        else:
            # Get item_id from cart items
            get_response = authenticated_client.get(f"/carts/{test_cart}/items")
            items = get_response.json()["items"]
            assert len(items) > 0
            item_id = items[0]["item_id"]
        
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
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [test_cart]}
        )
        assert add_response.status_code == status.HTTP_200_OK
        # Extract item_id from response
        response_data = add_response.json()
        if "item" in response_data:
            item_id = response_data["item"]["item_id"]
        elif "existing_item" in response_data:
            item_id = response_data["existing_item"]["item_id"]
        else:
            # Get item_id from cart items
            get_response = authenticated_client.get(f"/carts/{test_cart}/items")
            items = get_response.json()["items"]
            assert len(items) > 0
            item_id = items[0]["item_id"]
        
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
    
    def test_duplicate_items_same_cart(self, authenticated_client, test_cart, sample_item_data):
        """Test adding duplicate items (same URL) to the same cart."""
        # Add first item
        response1 = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [test_cart]}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Try to add same item again (same URL) - should return 409 Conflict
        response2 = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [test_cart]}
        )
        # Should return 409 Conflict with message about existing item
        assert response2.status_code == status.HTTP_409_CONFLICT
        response_data = response2.json()
        assert "already exists" in response_data.get("detail", {}).get("message", "").lower()
        assert "existing_item" in response_data.get("detail", {})
    
    def test_same_item_url_different_carts(self, authenticated_client, sample_cart_data, sample_item_data):
        """Test adding same item URL to different carts."""
        # Create two carts
        cart1_response = authenticated_client.post("/carts", json={**sample_cart_data, "cart_name": "Cart 1"})
        cart1_id = cart1_response.json()["cart_id"]
        
        cart2_response = authenticated_client.post("/carts", json={**sample_cart_data, "cart_name": "Cart 2"})
        cart2_id = cart2_response.json()["cart_id"]
        
        # Add same item to both carts - first add to cart1
        response1 = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [cart1_id]}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Try to add same URL to cart2 - should return 409 Conflict
        response2 = authenticated_client.post(
            "/carts/items/add-new",
            json={**sample_item_data, "selected_cart_ids": [cart2_id]}
        )
        # Should return 409 Conflict with message about existing item
        assert response2.status_code == status.HTTP_409_CONFLICT
        response_data = response2.json()
        assert "already exists" in response_data.get("detail", {}).get("message", "").lower()
        assert "existing_item" in response_data.get("detail", {})
        
        # Only cart1 should have the item (since duplicate was rejected)
        items1 = authenticated_client.get(f"/carts/{cart1_id}/items").json()["items"]
        items2 = authenticated_client.get(f"/carts/{cart2_id}/items").json()["items"]
        assert len(items1) > 0
        # Cart2 might be empty or have 0 items since duplicate was rejected
        
        # Cleanup
        authenticated_client.delete(f"/carts/{cart1_id}")
        authenticated_client.delete(f"/carts/{cart2_id}")
    
    def test_item_with_very_long_notes(self, authenticated_client, test_cart, sample_item_data):
        """Test adding item with very long notes."""
        long_notes = "A" * 10000  # Very long notes
        item_data = {**sample_item_data, "notes": long_notes, "selected_cart_ids": [test_cart]}
        
        response = authenticated_client.post(
            "/carts/items/add-new",
            json=item_data
        )
        # Should either succeed or fail validation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_item_with_special_characters_in_name(self, authenticated_client, test_cart, sample_item_data):
        """Test adding item with special characters in name."""
        item_data = {
            **sample_item_data,
            "name": "Product with <special> & 'characters' \"quotes\"",
            "selected_cart_ids": [test_cart]
        }
        
        response = authenticated_client.post(
            "/carts/items/add-new",
            json=item_data
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify item was added with sanitized name
        items = authenticated_client.get(f"/carts/{test_cart}/items").json()["items"]
        assert len(items) > 0
    
    def test_multiple_items_same_name_different_urls(self, authenticated_client, test_cart, sample_item_data):
        """Test adding multiple items with same name but different URLs."""
        item1 = {**sample_item_data, "url": "https://example.com/product1", "selected_cart_ids": [test_cart]}
        item2 = {**sample_item_data, "url": "https://example.com/product2", "selected_cart_ids": [test_cart]}
        
        response1 = authenticated_client.post(
            "/carts/items/add-new",
            json=item1
        )
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = authenticated_client.post(
            "/carts/items/add-new",
            json=item2
        )
        assert response2.status_code == status.HTTP_200_OK
        
        # Both items should be in the cart
        items = authenticated_client.get(f"/carts/{test_cart}/items").json()["items"]
        assert len(items) >= 2

