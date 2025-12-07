"""
Unit tests for data models (ItemInDB and Cart).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.item import ItemInDB
from app.models.cart import Cart


class TestItemInDB:
    """Test suite for ItemInDB model."""
    
    def test_from_mongo_valid_document(self):
        """Test converting valid MongoDB document to ItemInDB."""
        doc = {
            "item_id": "test-item-id-123",
            "name": "Test Product",
            "price": "99.99",
            "image": "https://example.com/image.jpg",
            "url": "https://example.com/product",
            "notes": "Test notes",
            "added_at": "2024-01-01T00:00:00",
            "selected_cart_ids": ["cart-1", "cart-2"]
        }
        
        item = ItemInDB.from_mongo(doc)
        
        assert item.item_id == "test-item-id-123"
        assert item.name == "Test Product"
        assert item.price == "99.99"
        assert item.image == "https://example.com/image.jpg"
        assert item.url == "https://example.com/product"
        assert item.notes == "Test notes"
        assert item.added_at == "2024-01-01T00:00:00"
        assert item.selected_cart_ids == ["cart-1", "cart-2"]
    
    def test_from_mongo_missing_optional_fields(self):
        """Test converting MongoDB document with missing optional fields."""
        doc = {
            "item_id": "test-item-id",
            "name": "Test Product",
            "price": "99.99",
            "added_at": "2024-01-01T00:00:00"
            # Missing: image, url, notes, selected_cart_ids
        }
        
        item = ItemInDB.from_mongo(doc)
        
        assert item.item_id == "test-item-id"
        assert item.name == "Test Product"
        assert item.price == "99.99"
        assert item.image is None
        assert item.url is None
        assert item.notes is None
        assert item.selected_cart_ids is None
    
    def test_from_mongo_url_string_conversion(self):
        """Test that URL fields are converted to strings."""
        doc = {
            "item_id": "test-item-id",
            "name": "Test Product",
            "price": "99.99",
            "image": "https://example.com/image.jpg",  # Already string
            "url": "https://example.com/product",  # Already string
            "added_at": "2024-01-01T00:00:00"
        }
        
        item = ItemInDB.from_mongo(doc)
        
        assert isinstance(item.image, str)
        assert isinstance(item.url, str)
    
    def test_from_mongo_does_not_mutate_original(self):
        """Test that from_mongo doesn't mutate the original dictionary."""
        original_doc = {
            "item_id": "test-item-id",
            "name": "Test Product",
            "price": "99.99",
            "image": "https://example.com/image.jpg",
            "added_at": "2024-01-01T00:00:00"
        }
        
        doc_copy = original_doc.copy()
        item = ItemInDB.from_mongo(doc_copy)
        
        # Modify item - should not affect original
        item.name = "Modified"
        
        assert original_doc["name"] == "Test Product"
    
    def test_to_mongo_dict(self):
        """Test converting ItemInDB to MongoDB dictionary."""
        item = ItemInDB(
            item_id="test-item-id",
            name="Test Product",
            price="99.99",
            image="https://example.com/image.jpg",
            url="https://example.com/product",
            notes="Test notes",
            added_at="2024-01-01T00:00:00",
            selected_cart_ids=["cart-1", "cart-2"]
        )
        
        mongo_dict = item.to_mongo_dict()
        
        assert isinstance(mongo_dict, dict)
        assert mongo_dict["item_id"] == "test-item-id"
        assert mongo_dict["name"] == "Test Product"
        assert mongo_dict["price"] == "99.99"
        assert mongo_dict["image"] == "https://example.com/image.jpg"
        assert mongo_dict["url"] == "https://example.com/product"
        assert mongo_dict["notes"] == "Test notes"
        assert mongo_dict["added_at"] == "2024-01-01T00:00:00"
        assert mongo_dict["selected_cart_ids"] == ["cart-1", "cart-2"]
    
    def test_to_mongo_dict_with_none_values(self):
        """Test to_mongo_dict includes None values."""
        item = ItemInDB(
            item_id="test-item-id",
            name="Test Product",
            price="99.99",
            added_at="2024-01-01T00:00:00",
            image=None,
            url=None,
            notes=None
        )
        
        mongo_dict = item.to_mongo_dict()
        
        # None values should be included (exclude_none=False)
        assert "image" in mongo_dict
        assert "url" in mongo_dict
        assert "notes" in mongo_dict
    
    def test_field_validation_name(self):
        """Test name field validation."""
        # Valid name
        item = ItemInDB(
            item_id="test-id",
            name="Valid Product Name",
            price="99.99",
            added_at="2024-01-01T00:00:00"
        )
        assert item.name == "Valid Product Name"
        
        # Empty name should raise ValidationError
        with pytest.raises(ValidationError):
            ItemInDB(
                item_id="test-id",
                name="",
                price="99.99",
                added_at="2024-01-01T00:00:00"
            )
    
    def test_field_validation_price(self):
        """Test price field validation."""
        # Valid price
        item = ItemInDB(
            item_id="test-id",
            name="Test Product",
            price="99.99",
            added_at="2024-01-01T00:00:00"
        )
        assert item.price == "99.99"
        
        # Empty price should raise ValidationError
        with pytest.raises(ValidationError):
            ItemInDB(
                item_id="test-id",
                name="Test Product",
                price="",
                added_at="2024-01-01T00:00:00"
            )
    
    def test_field_validation_notes(self):
        """Test notes field validation."""
        # Valid notes
        item = ItemInDB(
            item_id="test-id",
            name="Test Product",
            price="99.99",
            added_at="2024-01-01T00:00:00",
            notes="Valid notes"
        )
        assert item.notes == "Valid notes"
        
        # None notes should be allowed
        item = ItemInDB(
            item_id="test-id",
            name="Test Product",
            price="99.99",
            added_at="2024-01-01T00:00:00",
            notes=None
        )
        assert item.notes is None
    
    def test_round_trip_conversion(self):
        """Test that from_mongo -> to_mongo_dict maintains data integrity."""
        original_doc = {
            "item_id": "test-item-id",
            "name": "Test Product",
            "price": "99.99",
            "image": "https://example.com/image.jpg",
            "url": "https://example.com/product",
            "notes": "Test notes",
            "added_at": "2024-01-01T00:00:00",
            "selected_cart_ids": ["cart-1"]
        }
        
        item = ItemInDB.from_mongo(original_doc)
        mongo_dict = item.to_mongo_dict()
        
        # Check all fields match
        assert mongo_dict["item_id"] == original_doc["item_id"]
        assert mongo_dict["name"] == original_doc["name"]
        assert mongo_dict["price"] == original_doc["price"]
        assert mongo_dict["image"] == original_doc["image"]
        assert mongo_dict["url"] == original_doc["url"]
        assert mongo_dict["notes"] == original_doc["notes"]
        assert mongo_dict["added_at"] == original_doc["added_at"]
        assert mongo_dict["selected_cart_ids"] == original_doc["selected_cart_ids"]


class TestCart:
    """Test suite for Cart model."""
    
    def test_from_mongo_empty_items(self):
        """Test converting MongoDB document with empty items list."""
        doc = {
            "cart_id": "test-cart-id",
            "cart_name": "Test Cart",
            "item_count": 0,
            "created_at": "2024-01-01T00:00:00",
            "items": []
        }
        
        cart = Cart.from_mongo(doc)
        
        assert cart.cart_id == "test-cart-id"
        assert cart.cart_name == "Test Cart"
        assert cart.item_count == 0
        assert cart.created_at == "2024-01-01T00:00:00"
        assert isinstance(cart.items, list)
        assert len(cart.items) == 0
    
    def test_from_mongo_with_items(self):
        """Test converting MongoDB document with nested items."""
        doc = {
            "cart_id": "test-cart-id",
            "cart_name": "Test Cart",
            "item_count": 2,
            "created_at": "2024-01-01T00:00:00",
            "items": [
                {
                    "item_id": "item-1",
                    "name": "Product 1",
                    "price": "99.99",
                    "added_at": "2024-01-01T00:00:00"
                },
                {
                    "item_id": "item-2",
                    "name": "Product 2",
                    "price": "149.99",
                    "image": "https://example.com/image2.jpg",
                    "added_at": "2024-01-01T01:00:00"
                }
            ]
        }
        
        cart = Cart.from_mongo(doc)
        
        assert cart.cart_id == "test-cart-id"
        assert cart.item_count == 2
        assert len(cart.items) == 2
        
        # Check items are ItemInDB objects
        assert isinstance(cart.items[0], ItemInDB)
        assert isinstance(cart.items[1], ItemInDB)
        assert cart.items[0].item_id == "item-1"
        assert cart.items[1].item_id == "item-2"
    
    def test_to_mongo_dict_empty_items(self):
        """Test converting Cart to MongoDB dict with empty items."""
        cart = Cart(
            cart_id="test-cart-id",
            cart_name="Test Cart",
            item_count=0,
            created_at="2024-01-01T00:00:00",
            items=[]
        )
        
        mongo_dict = cart.to_mongo_dict()
        
        assert isinstance(mongo_dict, dict)
        assert mongo_dict["cart_id"] == "test-cart-id"
        assert mongo_dict["cart_name"] == "Test Cart"
        assert mongo_dict["item_count"] == 0
        assert mongo_dict["created_at"] == "2024-01-01T00:00:00"
        assert isinstance(mongo_dict["items"], list)
        assert len(mongo_dict["items"]) == 0
    
    def test_to_mongo_dict_with_items(self):
        """Test converting Cart to MongoDB dict with nested items."""
        items = [
            ItemInDB(
                item_id="item-1",
                name="Product 1",
                price="99.99",
                added_at="2024-01-01T00:00:00"
            ),
            ItemInDB(
                item_id="item-2",
                name="Product 2",
                price="149.99",
                image="https://example.com/image2.jpg",
                added_at="2024-01-01T01:00:00"
            )
        ]
        
        cart = Cart(
            cart_id="test-cart-id",
            cart_name="Test Cart",
            item_count=2,
            created_at="2024-01-01T00:00:00",
            items=items
        )
        
        mongo_dict = cart.to_mongo_dict()
        
        assert len(mongo_dict["items"]) == 2
        assert isinstance(mongo_dict["items"][0], dict)
        assert isinstance(mongo_dict["items"][1], dict)
        assert mongo_dict["items"][0]["item_id"] == "item-1"
        assert mongo_dict["items"][1]["item_id"] == "item-2"
    
    def test_round_trip_conversion_with_items(self):
        """Test that from_mongo -> to_mongo_dict maintains nested items."""
        original_doc = {
            "cart_id": "test-cart-id",
            "cart_name": "Test Cart",
            "item_count": 1,
            "created_at": "2024-01-01T00:00:00",
            "items": [
                {
                    "item_id": "item-1",
                    "name": "Product 1",
                    "price": "99.99",
                    "added_at": "2024-01-01T00:00:00"
                }
            ]
        }
        
        cart = Cart.from_mongo(original_doc)
        mongo_dict = cart.to_mongo_dict()
        
        assert mongo_dict["cart_id"] == original_doc["cart_id"]
        assert mongo_dict["cart_name"] == original_doc["cart_name"]
        assert mongo_dict["item_count"] == original_doc["item_count"]
        assert len(mongo_dict["items"]) == 1
        assert mongo_dict["items"][0]["item_id"] == "item-1"
        assert mongo_dict["items"][0]["name"] == "Product 1"
    
    def test_cart_model_instantiation(self):
        """Test Cart model can be instantiated with all fields."""
        items = [
            ItemInDB(
                item_id="item-1",
                name="Product 1",
                price="99.99",
                added_at="2024-01-01T00:00:00"
            )
        ]
        
        cart = Cart(
            cart_id="test-cart-id",
            cart_name="Test Cart",
            item_count=1,
            created_at="2024-01-01T00:00:00",
            items=items
        )
        
        assert cart.cart_id == "test-cart-id"
        assert cart.cart_name == "Test Cart"
        assert cart.item_count == 1
        assert len(cart.items) == 1

