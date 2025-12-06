"""
Pytest configuration and shared fixtures for BuyHive backend tests.
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Generator, AsyncGenerator
import os
import copy
from jose import jwt
from datetime import datetime, timedelta

from main import app
from app.config.settings import settings


# Test user data
TEST_USER_EMAIL = "test@buyhive.com"
TEST_USER_NAME = "Test User"
TEST_AUTH0_ID = "auth0|test123456"


@pytest.fixture
def mock_auth0_token() -> str:
    """
    Generate a mock Auth0 JWT token for testing.
    In real tests, you'd use actual Auth0 tokens or mock the verification.
    """
    # Create a simple mock token payload
    payload = {
        "iss": f"https://{settings.AUTH0_DOMAIN}/",
        "sub": TEST_AUTH0_ID,
        "aud": settings.AUTH0_AUDIENCE,
        "email": TEST_USER_EMAIL,
        "name": TEST_USER_NAME,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        "scope": "openid profile email",
    }
    
    # For testing, we'll mock the token verification instead of creating real tokens
    # This token won't actually verify, but our mocks will handle it
    return "mock_token_for_testing"


@pytest.fixture
def mock_verify_token():
    """
    Mock the Auth0 token verification to return a test user payload.
    """
    async def mock_verify(token: str):
        return {
            "iss": f"https://{settings.AUTH0_DOMAIN}/",
            "sub": TEST_AUTH0_ID,
            "aud": settings.AUTH0_AUDIENCE,
            "email": TEST_USER_EMAIL,
            "name": TEST_USER_NAME,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        }
    
    return mock_verify


@pytest.fixture
def mock_get_or_create_user():
    """
    Mock the get_or_create_user_from_token function.
    """
    async def mock_get_user(payload: dict):
        return {
            "email": TEST_USER_EMAIL,
            "name": TEST_USER_NAME,
            "auth0_id": TEST_AUTH0_ID,
        }
    
    return mock_get_user


@pytest.fixture
def mock_user_in_db():
    """
    Mock user data as it would appear in the database.
    """
    return {
        "email": TEST_USER_EMAIL,
        "name": TEST_USER_NAME,
        "auth0_id": TEST_AUTH0_ID,
        "cart_count": 0,
        "carts": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


class MockUpdateResult:
    """Mock MongoDB update result object."""
    def __init__(self, modified_count=1, matched_count=1, upserted_id=None):
        self.modified_count = modified_count
        self.matched_count = matched_count
        self.upserted_id = upserted_id


@pytest.fixture
def authenticated_client(mock_verify_token, mock_get_or_create_user, mock_user_in_db) -> Generator:
    """
    Create a test client with mocked authentication and stateful database.
    All requests will be treated as authenticated with TEST_USER_EMAIL.
    """
    from app.functions.database import cart_collection
    from uuid import uuid4
    
    # Track state for the mock database - create fresh state for each test
    # Don't use mock_user_in_db directly to avoid any shared state issues
    db_state = {
        "users": {
            TEST_USER_EMAIL: {
                "email": TEST_USER_EMAIL,
                "name": TEST_USER_NAME,
                "auth0_id": TEST_AUTH0_ID,
                "cart_count": 0,
                "carts": [],  # Always start with empty carts
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        }
    }
    
    async def mock_find_one(query: dict, projection=None):
        email = query.get("email")
        if not email or email not in db_state["users"]:
            return None
        
        user_data = copy.deepcopy(db_state["users"][email])
        
        # Handle cart name queries FIRST (checking if cart with name exists)
        # This is the most specific check, so do it first
        cart_name_key = "carts.cart_name"
        if cart_name_key in query:
            cart_name = query[cart_name_key]
            carts_list = user_data.get("carts", [])
            # Explicitly check if carts list is empty or None
            if not carts_list or len(carts_list) == 0:
                return None  # No carts exist, so definitely no cart with this name
            # Check if any cart has this name
            found = False
            for cart in carts_list:
                if isinstance(cart, dict) and cart.get("cart_name") == cart_name:
                    found = True
                    break
            if found:
                return user_data  # Cart exists
            else:
                return None  # No cart with this name found
        
        # Handle cart-specific queries
        if "carts.cart_id" in query:
            cart_id = query["carts.cart_id"]
            matching_carts = [c for c in user_data.get("carts", []) if c.get("cart_id") == cart_id]
            if matching_carts:
                user_data["carts"] = matching_carts
            else:
                return None
        
        # Handle item-specific queries
        if "carts.items.item_id" in query:
            item_id = query["carts.items.item_id"]
            # Return user with carts containing the item
            filtered_carts = []
            for cart in user_data.get("carts", []):
                if any(i.get("item_id") == item_id for i in cart.get("items", [])):
                    filtered_carts.append(cart)
            user_data["carts"] = filtered_carts
        
        # Handle item URL queries
        if "carts.items.url" in query:
            url = query["carts.items.url"]
            for cart in user_data.get("carts", []):
                if any(i.get("url") == url for i in cart.get("items", [])):
                    return user_data
            return None
        
        return user_data
    
    async def mock_update_one(filter_query: dict, update_op: dict, upsert=False):
        email = filter_query.get("email")
        if not email:
            return MockUpdateResult(modified_count=0, matched_count=0)
        
        # Create user if upsert and doesn't exist
        if upsert and email not in db_state["users"]:
            db_state["users"][email] = {
                "email": email,
                "carts": [],
                "cart_count": 0,
                "created_at": datetime.utcnow().isoformat(),
            }
        
        if email not in db_state["users"]:
            return MockUpdateResult(modified_count=0, matched_count=0)
        
        user = db_state["users"][email]
        modified = False
        
        # Handle $push operations (add cart/item)
        if "$push" in update_op:
            push_data = update_op["$push"]
            if "carts" in push_data:
                # Adding a new cart
                new_cart = push_data["carts"].copy()
                if "cart_id" not in new_cart:
                    new_cart["cart_id"] = str(uuid4())
                if "carts" not in user:
                    user["carts"] = []
                user["carts"].append(new_cart)
                modified = True
                return MockUpdateResult(modified_count=1, upserted_id="new_cart_id" if upsert else None)
            elif "carts.$.items" in push_data:
                # Adding item to cart
                cart_id = filter_query.get("carts.cart_id")
                new_item = push_data["carts.$.items"].copy()
                if "item_id" not in new_item:
                    new_item["item_id"] = str(uuid4())
                for cart in user.get("carts", []):
                    if cart.get("cart_id") == cart_id:
                        if "items" not in cart:
                            cart["items"] = []
                        cart["items"].append(new_item)
                        cart["item_count"] = cart.get("item_count", 0) + 1
                        modified = True
                        return MockUpdateResult(modified_count=1)
        
        # Handle $pull operations (remove cart/item)
        if "$pull" in update_op:
            pull_data = update_op["$pull"]
            if "carts" in pull_data:
                # Removing a cart
                cart_id = pull_data["carts"].get("cart_id")
                original_count = len(user.get("carts", []))
                user["carts"] = [c for c in user.get("carts", []) if c.get("cart_id") != cart_id]
                if len(user["carts"]) < original_count:
                    modified = True
                    return MockUpdateResult(modified_count=1)
            elif "carts.$.items" in pull_data:
                # Removing item from cart
                cart_id = filter_query.get("carts.cart_id")
                item_id = pull_data["carts.$.items"].get("item_id")
                for cart in user.get("carts", []):
                    if cart.get("cart_id") == cart_id:
                        original_item_count = len(cart.get("items", []))
                        cart["items"] = [i for i in cart.get("items", []) if i.get("item_id") != item_id]
                        if len(cart["items"]) < original_item_count:
                            cart["item_count"] = cart.get("item_count", 0) - 1
                            modified = True
                            return MockUpdateResult(modified_count=1)
        
        # Handle $set operations
        if "$set" in update_op:
            set_data = update_op["$set"]
            if "carts.$.cart_name" in set_data:
                cart_id = filter_query.get("carts.cart_id")
                new_name = set_data["carts.$.cart_name"]
                for cart in user.get("carts", []):
                    if cart.get("cart_id") == cart_id:
                        cart["cart_name"] = new_name
                        modified = True
                        return MockUpdateResult(modified_count=1)
        
        # Handle $inc operations
        if "$inc" in update_op:
            inc_data = update_op["$inc"]
            if "cart_count" in inc_data:
                user["cart_count"] = user.get("cart_count", 0) + inc_data["cart_count"]
                modified = True
            elif "carts.$.item_count" in inc_data:
                cart_id = filter_query.get("carts.cart_id")
                for cart in user.get("carts", []):
                    if cart.get("cart_id") == cart_id:
                        cart["item_count"] = cart.get("item_count", 0) + inc_data["carts.$.item_count"]
                        modified = True
        
        return MockUpdateResult(modified_count=1 if modified else 0)
    
    async def mock_update_many(filter_query: dict, update_op: dict, array_filters=None):
        # Simplified for now - can be enhanced if needed
        email = filter_query.get("email")
        if email and email in db_state["users"]:
            # Handle array filter updates (like updating item notes across all carts)
            if "$set" in update_op and array_filters:
                set_data = update_op["$set"]
                user = db_state["users"][email]
                modified = False
                for cart in user.get("carts", []):
                    for item in cart.get("items", []):
                        # Check if item matches array filter
                        for af in array_filters:
                            if "item.item_id" in af:
                                item_id = af["item.item_id"]
                                if item.get("item_id") == item_id:
                                    # Apply the update
                                    for key, value in set_data.items():
                                        if "items.$[item]" in key:
                                            field = key.split(".")[-1]
                                            item[field] = value
                                            modified = True
                return MockUpdateResult(modified_count=1 if modified else 0)
        return MockUpdateResult(modified_count=0)
    
    # Create the mock collection
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(side_effect=mock_find_one)
    mock_collection.update_one = AsyncMock(side_effect=mock_update_one)
    mock_collection.update_many = AsyncMock(side_effect=mock_update_many)
    mock_collection.insert_one = AsyncMock()
    mock_collection.delete_one = AsyncMock()
    
    # Import the modules to patch them
    import app.auth.auth0 as auth0_module
    import app.auth.dependencies as deps_module
    import app.functions.database as db_module
    import app.functions.cart as cart_module
    import app.functions.item as item_module
    
    # Patch where the functions are used (in dependencies module and where imported)
    with patch.object(auth0_module, "verify_auth0_token", side_effect=mock_verify_token):
        with patch.object(auth0_module, "get_or_create_user_from_token", side_effect=mock_get_or_create_user):
            with patch.object(deps_module, "verify_auth0_token", side_effect=mock_verify_token):
                with patch.object(deps_module, "get_or_create_user_from_token", side_effect=mock_get_or_create_user):
                    with patch.object(db_module, "cart_collection", mock_collection):
                        with patch.object(deps_module, "cart_collection", mock_collection):
                            with patch.object(cart_module, "cart_collection", mock_collection):
                                with patch.object(item_module, "cart_collection", mock_collection):
                                    with TestClient(app) as client:
                                        # Store auth headers for use in requests
                                        auth_headers = {"Authorization": "Bearer mock_token_for_testing"}
                                        client._auth_headers = auth_headers
                                        
                                        # Save original methods BEFORE patching (to avoid recursion)
                                        original_get = client.get
                                        original_post = client.post
                                        original_put = client.put
                                        original_delete = client.delete
                                        
                                        # Helper methods that call the ORIGINAL methods (not the patched ones)
                                        def _get(url, **kwargs):
                                            kwargs.setdefault("headers", {}).update(auth_headers)
                                            return original_get(url, **kwargs)
                                        
                                        def _post(url, **kwargs):
                                            kwargs.setdefault("headers", {}).update(auth_headers)
                                            return original_post(url, **kwargs)
                                        
                                        def _put(url, **kwargs):
                                            kwargs.setdefault("headers", {}).update(auth_headers)
                                            return original_put(url, **kwargs)
                                        
                                        def _delete(url, **kwargs):
                                            kwargs.setdefault("headers", {}).update(auth_headers)
                                            return original_delete(url, **kwargs)
                                        
                                        # NOW we can safely monkey patch (the wrappers call original methods)
                                        client.get = _get
                                        client.post = _post
                                        client.put = _put
                                        client.delete = _delete
                                        
                                        yield client


@pytest.fixture
@pytest.mark.asyncio
async def async_authenticated_client(mock_verify_token, mock_get_or_create_user) -> AsyncGenerator:
    """
    Create an async test client with mocked authentication.
    Note: Most tests use TestClient (synchronous), this is for async-specific tests.
    """
    with patch("app.auth.auth0.verify_auth0_token", side_effect=mock_verify_token):
        with patch("app.auth.auth0.get_or_create_user_from_token", side_effect=mock_get_or_create_user):
            async with AsyncClient(app=app, base_url="http://test") as client:
                client.headers = {"Authorization": "Bearer mock_token_for_testing"}
                yield client


@pytest.fixture
def unauthenticated_client() -> Generator:
    """
    Create a test client without authentication.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """
    Cleanup fixture that runs after each test.
    Can be used to clean up test data from database.
    """
    yield
    # Add cleanup logic here if needed
    # For now, tests should clean up their own data


@pytest.fixture
def sample_cart_data() -> dict:
    """Sample cart data for testing."""
    return {
        "cart_name": "Test Cart"
    }


@pytest.fixture
def sample_item_data() -> dict:
    """Sample item data for testing."""
    return {
        "name": "Test Product",
        "price": "99.99",
        "image": "https://example.com/image.jpg",
        "url": "https://example.com/product",
        "notes": "Test notes"
    }

