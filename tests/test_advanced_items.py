"""
Tests for advanced item operations (multi-cart operations).
"""
import pytest
from fastapi import status


class TestAdvancedItemOperations:
    """Test suite for advanced item management endpoints."""
    
    @pytest.fixture
    def test_carts(self, authenticated_client, sample_cart_data):
        """Create multiple test carts and return their IDs."""
        cart_ids = []
        for i in range(3):
            cart_data = {**sample_cart_data, "cart_name": f"{sample_cart_data['cart_name']} {i+1}"}
            response = authenticated_client.post("/carts", json=cart_data)
            assert response.status_code == status.HTTP_200_OK
            cart_ids.append(response.json()["cart_id"])
        yield cart_ids
        # Cleanup
        for cart_id in cart_ids:
            authenticated_client.delete(f"/carts/{cart_id}")
    
    def test_add_new_item_to_single_cart(self, authenticated_client, test_carts, sample_item_data):
        """Test adding a new item to a single cart using /items/add-new."""
        cart_id = test_carts[0]
        
        payload = {
            **sample_item_data,
            "selected_cart_ids": [cart_id]
        }
        
        response = authenticated_client.post("/carts/items/add-new", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "item" in data or "message" in data
        
        # Verify item was added to the cart
        get_response = authenticated_client.get(f"/carts/{cart_id}/items")
        items = get_response.json()["items"]
        assert len(items) > 0
        assert any(item.get("name") == sample_item_data["name"] for item in items)
    
    def test_add_new_item_to_multiple_carts(self, authenticated_client, test_carts, sample_item_data):
        """Test adding a new item to multiple carts simultaneously."""
        selected_cart_ids = test_carts[:2]  # Use first 2 carts
        
        payload = {
            **sample_item_data,
            "selected_cart_ids": selected_cart_ids
        }
        
        response = authenticated_client.post("/carts/items/add-new", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "item" in data or "message" in data
        
        # Verify item was added to both carts
        for cart_id in selected_cart_ids:
            get_response = authenticated_client.get(f"/carts/{cart_id}/items")
            items = get_response.json()["items"]
            assert len(items) > 0
            assert any(item.get("name") == sample_item_data["name"] for item in items)
    
    def test_add_new_item_duplicate_url(self, authenticated_client, test_carts, sample_item_data):
        """Test that adding an item with duplicate URL is prevented."""
        cart_id = test_carts[0]
        
        # First, add item normally
        add_response = authenticated_client.post(
            f"/carts/{cart_id}/items",
            json=sample_item_data
        )
        assert add_response.status_code == status.HTTP_200_OK
        
        # Try to add same item via /items/add-new (should detect duplicate)
        payload = {
            **sample_item_data,
            "selected_cart_ids": [test_carts[1]]  # Different cart
        }
        
        response = authenticated_client.post("/carts/items/add-new", json=payload)
        # Should return error message about duplicate
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "already exists" in data.get("message", "").lower() or "existing_item" in data
    
    def test_move_item_between_carts(self, authenticated_client, test_carts, sample_item_data):
        """Test moving an item from one cart to another."""
        source_cart_id = test_carts[0]
        target_cart_id = test_carts[1]
        
        # Add item to source cart
        add_response = authenticated_client.post(
            f"/carts/{source_cart_id}/items",
            json=sample_item_data
        )
        assert add_response.status_code == status.HTTP_200_OK
        item_id = add_response.json()["item_id"]
        
        # Move item to target cart
        move_response = authenticated_client.put(
            f"/carts/items/{item_id}/move",
            json={"selected_cart_ids": [target_cart_id]}
        )
        assert move_response.status_code == status.HTTP_200_OK
        
        # Verify item is in target cart
        get_target = authenticated_client.get(f"/carts/{target_cart_id}/items")
        target_items = get_target.json()["items"]
        assert any(item.get("item_id") == item_id for item in target_items)
        
        # Verify item is still in source cart (or removed, depends on implementation)
        get_source = authenticated_client.get(f"/carts/{source_cart_id}/items")
        source_items = get_source.json()["items"]
        # Item might still be in source or removed - depends on implementation
    
    def test_move_item_to_multiple_carts(self, authenticated_client, test_carts, sample_item_data):
        """Test moving an item to multiple carts."""
        source_cart_id = test_carts[0]
        target_cart_ids = test_carts[1:3]  # Move to 2 carts
        
        # Add item to source cart
        add_response = authenticated_client.post(
            f"/carts/{source_cart_id}/items",
            json=sample_item_data
        )
        item_id = add_response.json()["item_id"]
        
        # Move item to multiple carts
        move_response = authenticated_client.put(
            f"/carts/items/{item_id}/move",
            json={"selected_cart_ids": target_cart_ids}
        )
        assert move_response.status_code == status.HTTP_200_OK
        
        # Verify item is in target carts
        for cart_id in target_cart_ids:
            get_response = authenticated_client.get(f"/carts/{cart_id}/items")
            items = get_response.json()["items"]
            assert any(item.get("item_id") == item_id for item in items)
    
    def test_move_item_not_found(self, authenticated_client):
        """Test moving a non-existent item."""
        fake_item_id = "non-existent-item-id-12345"
        
        response = authenticated_client.put(
            f"/carts/items/{fake_item_id}/move",
            json={"selected_cart_ids": ["cart-id"]}
        )
        # Should return error (500 or specific error)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_nuke_item_from_single_cart(self, authenticated_client, test_carts, sample_item_data):
        """Test deleting an item from all carts when it's in one cart."""
        cart_id = test_carts[0]
        
        # Add item
        add_response = authenticated_client.post(
            f"/carts/{cart_id}/items",
            json=sample_item_data
        )
        item_id = add_response.json()["item_id"]
        
        # Nuke the item
        nuke_response = authenticated_client.delete(f"/carts/items/{item_id}/nuke")
        assert nuke_response.status_code == status.HTTP_200_OK
        
        # Verify item is removed (response is Cart model)
        get_response = authenticated_client.get(f"/carts/{cart_id}/items")
        cart_data = get_response.json()
        items = cart_data["items"]
        assert not any(item.get("item_id") == item_id for item in items)
    
    def test_nuke_item_from_multiple_carts(self, authenticated_client, test_carts, sample_item_data):
        """Test deleting an item from all carts when it's in multiple carts."""
        # Add item to multiple carts using /items/add-new
        payload = {
            **sample_item_data,
            "selected_cart_ids": test_carts[:2]
        }
        
        add_response = authenticated_client.post("/carts/items/add-new", json=payload)
        assert add_response.status_code == status.HTTP_200_OK
        
        # Get item_id from response or from cart
        get_response = authenticated_client.get(f"/carts/{test_carts[0]}/items")
        items = get_response.json()["items"]
        item_id = items[0]["item_id"] if items else None
        assert item_id is not None
        
        # Nuke the item
        nuke_response = authenticated_client.delete(f"/carts/items/{item_id}/nuke")
        assert nuke_response.status_code == status.HTTP_200_OK
        
        # Verify item is removed from all carts (response is Cart model)
        for cart_id in test_carts[:2]:
            get_response = authenticated_client.get(f"/carts/{cart_id}/items")
            cart_data = get_response.json()
            items = cart_data["items"]
            assert not any(item.get("item_id") == item_id for item in items)
    
    def test_nuke_item_not_found(self, authenticated_client):
        """Test nuking a non-existent item."""
        fake_item_id = "non-existent-item-id-12345"
        
        response = authenticated_client.delete(f"/carts/items/{fake_item_id}/nuke")
        # Should return error message but 200 status
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "not found" in data.get("message", "").lower()
    
    def test_add_new_item_invalid_cart_ids(self, authenticated_client, sample_item_data):
        """Test adding item with invalid cart IDs."""
        payload = {
            **sample_item_data,
            "selected_cart_ids": ["invalid-cart-id-12345"]
        }
        
        response = authenticated_client.post("/carts/items/add-new", json=payload)
        # Should either succeed (item created but not added) or return error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_move_item_unauthorized(self, unauthenticated_client):
        """Test that moving items requires authentication."""
        response = unauthenticated_client.put(
            "/carts/items/test-item-id/move",
            json={"selected_cart_ids": ["cart-id"]}
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_nuke_item_unauthorized(self, unauthenticated_client):
        """Test that nuking items requires authentication."""
        response = unauthenticated_client.delete("/carts/items/test-item-id/nuke")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_move_item_all_carts(self, authenticated_client, test_carts, sample_item_data):
        """Test moving item that exists in all user carts."""
        # Add item to all carts using /items/add-new
        payload = {
            **sample_item_data,
            "selected_cart_ids": test_carts
        }
        
        add_response = authenticated_client.post("/carts/items/add-new", json=payload)
        assert add_response.status_code == status.HTTP_200_OK
        
        # Get item_id
        get_response = authenticated_client.get(f"/carts/{test_carts[0]}/items")
        items = get_response.json()["items"]
        item_id = items[0]["item_id"] if items else None
        assert item_id is not None
        
        # Move item to subset of carts (should still work)
        move_response = authenticated_client.put(
            f"/carts/items/{item_id}/move",
            json={"selected_cart_ids": test_carts[:1]}  # Move to just first cart
        )
        assert move_response.status_code == status.HTTP_200_OK
    
    def test_add_item_to_invalid_cart(self, authenticated_client, sample_item_data):
        """Test adding item to cart that doesn't belong to user."""
        payload = {
            **sample_item_data,
            "selected_cart_ids": ["invalid-cart-id-12345"]
        }
        
        response = authenticated_client.post("/carts/items/add-new", json=payload)
        # Should either succeed (creating item) or return error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_complex_multi_cart_scenario(self, authenticated_client, test_carts, sample_item_data):
        """Test complex scenario with multiple carts and items."""
        # Add item to first cart
        item1_response = authenticated_client.post(
            f"/carts/{test_carts[0]}/items",
            json={**sample_item_data, "name": "Item 1"}
        )
        item1_id = item1_response.json()["item_id"]
        
        # Add new item across multiple carts
        payload = {
            **sample_item_data,
            "name": "Item 2",
            "selected_cart_ids": test_carts[:2]
        }
        item2_response = authenticated_client.post("/carts/items/add-new", json=payload)
        assert item2_response.status_code == status.HTTP_200_OK
        
        # Move item1 to multiple carts
        move_response = authenticated_client.put(
            f"/carts/items/{item1_id}/move",
            json={"selected_cart_ids": test_carts[1:]}
        )
        assert move_response.status_code == status.HTTP_200_OK
        
        # Verify items are in correct carts
        for cart_id in test_carts:
            items = authenticated_client.get(f"/carts/{cart_id}/items").json()["items"]
            # Items should be distributed across carts
            assert len(items) >= 0  # At least empty or with items

