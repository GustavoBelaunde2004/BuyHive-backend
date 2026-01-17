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
from app.core.config import settings


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
    
    # Use AsyncMock with side_effect - AsyncMock automatically handles async functions
    mock = AsyncMock(side_effect=mock_verify)
    return mock


@pytest.fixture
def mock_get_or_create_user():
    """
    Mock the get_or_create_user_from_token function.
    """
    async def mock_get_user(payload: dict):
        return {
            "user_id": TEST_AUTH0_ID,
            "email": TEST_USER_EMAIL,
            "name": TEST_USER_NAME,
            "auth0_id": TEST_AUTH0_ID,
        }
    
    # Use AsyncMock with side_effect - AsyncMock automatically handles async functions
    mock = AsyncMock(side_effect=mock_get_user)
    return mock


@pytest.fixture
def mock_user_in_db():
    """
    Mock user data as it would appear in the database.
    """
    return {
        "user_id": TEST_AUTH0_ID,
        "email": TEST_USER_EMAIL,
        "name": TEST_USER_NAME,
        "auth0_id": TEST_AUTH0_ID,
        "cart_count": 0,
        "cart_ids": [],
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
    from uuid import uuid4
    
    # In-memory DB state for 3-collection model
    now = datetime.utcnow().isoformat()
    db_state = {
        "users": {
            TEST_AUTH0_ID: {
                "user_id": TEST_AUTH0_ID,
                "auth0_id": TEST_AUTH0_ID,
                "email": TEST_USER_EMAIL,
                "name": TEST_USER_NAME,
                "cart_count": 0,
                "cart_ids": [],
                "created_at": now,
                "updated_at": now,
            }
        },
        "carts": {},  # cart_id -> cart_doc
        "items": {},  # item_id -> item_doc
        "feedback": {},  # feedback_id -> feedback_doc
    }

    class MockInsertResult:
        def __init__(self, inserted_id="mock_id"):
            self.inserted_id = inserted_id

    class MockDeleteResult:
        def __init__(self, deleted_count=1):
            self.deleted_count = deleted_count

    class MockCursor:
        def __init__(self, docs):
            self._docs = docs

        async def to_list(self, length=None):
            return copy.deepcopy(self._docs)

    def _match_query(doc: dict, query: dict) -> bool:
        for k, v in query.items():
            if isinstance(v, dict) and "$in" in v:
                if doc.get(k) not in v["$in"]:
                    return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def _apply_update(doc: dict, update_op: dict):
        modified = False
        if "$set" in update_op:
            for k, v in update_op["$set"].items():
                if doc.get(k) != v:
                    doc[k] = v
                    modified = True
        if "$setOnInsert" in update_op:
            # handled by caller for upsert
            pass
        if "$inc" in update_op:
            for k, v in update_op["$inc"].items():
                doc[k] = int(doc.get(k, 0)) + int(v)
                modified = True
        if "$push" in update_op:
            for k, v in update_op["$push"].items():
                arr = doc.get(k) or []
                arr.append(v)
                doc[k] = arr
                modified = True
        if "$addToSet" in update_op:
            for k, v in update_op["$addToSet"].items():
                arr = doc.get(k) or []
                if v not in arr:
                    arr.append(v)
                    doc[k] = arr
                    modified = True
        if "$pull" in update_op:
            for k, v in update_op["$pull"].items():
                arr = doc.get(k) or []
                if v in arr:
                    arr = [x for x in arr if x != v]
                    doc[k] = arr
                    modified = True
        return modified

    class InMemoryCollection:
        def __init__(self, name: str):
            self.name = name

        async def find_one(self, query: dict, projection=None):
            if self.name == "users":
                for doc in db_state["users"].values():
                    if _match_query(doc, query):
                        return copy.deepcopy(doc)
                return None
            if self.name == "carts":
                for doc in db_state["carts"].values():
                    if _match_query(doc, query):
                        return copy.deepcopy(doc)
                return None
            if self.name == "items":
                for doc in db_state["items"].values():
                    if _match_query(doc, query):
                        return copy.deepcopy(doc)
                return None
            if self.name == "feedback":
                for doc in db_state["feedback"].values():
                    if _match_query(doc, query):
                        return copy.deepcopy(doc)
                return None
            return None

        def find(self, query: dict):
            if self.name == "carts":
                docs = [d for d in db_state["carts"].values() if _match_query(d, query)]
                return MockCursor(docs)
            if self.name == "items":
                # support $in on item_id
                docs = []
                for d in db_state["items"].values():
                    ok = True
                    for k, v in query.items():
                        if isinstance(v, dict) and "$in" in v:
                            if d.get(k) not in v["$in"]:
                                ok = False
                                break
                        else:
                            if d.get(k) != v:
                                ok = False
                                break
                    if ok:
                        docs.append(d)
                return MockCursor(docs)
            return MockCursor([])

        async def insert_one(self, doc: dict):
            if self.name == "users":
                db_state["users"][doc["user_id"]] = copy.deepcopy(doc)
            elif self.name == "carts":
                db_state["carts"][doc["cart_id"]] = copy.deepcopy(doc)
            elif self.name == "items":
                db_state["items"][doc["item_id"]] = copy.deepcopy(doc)
            elif self.name == "feedback":
                db_state["feedback"][doc["feedback_id"]] = copy.deepcopy(doc)
            return MockInsertResult()

        async def update_one(self, filter_query: dict, update_op: dict, upsert: bool = False):
            # Resolve collection and find target doc
            store = db_state[self.name]
            target_key = None
            target_doc = None

            if self.name == "users":
                # keyed by user_id
                for k, d in store.items():
                    if _match_query(d, filter_query):
                        target_key, target_doc = k, d
                        break
                if target_doc is None and upsert:
                    base = {}
                    base.update(update_op.get("$setOnInsert", {}))
                    base.update(update_op.get("$set", {}))
                    if "user_id" in filter_query:
                        base.setdefault("user_id", filter_query["user_id"])
                        base.setdefault("auth0_id", filter_query["user_id"])
                    base.setdefault("cart_ids", [])
                    base.setdefault("cart_count", 0)
                    store[base["user_id"]] = base
                    return MockUpdateResult(modified_count=1, matched_count=0, upserted_id="upserted")

            else:
                # carts/items keyed by id field
                for k, d in store.items():
                    if _match_query(d, filter_query):
                        target_key, target_doc = k, d
                        break

            if target_doc is None:
                return MockUpdateResult(modified_count=0, matched_count=0)

            modified = _apply_update(target_doc, update_op)
            store[target_key] = target_doc
            return MockUpdateResult(modified_count=1 if modified else 0, matched_count=1)

        async def delete_one(self, filter_query: dict):
            store = db_state[self.name]
            delete_keys = []
            for k, d in store.items():
                if _match_query(d, filter_query):
                    delete_keys.append(k)
                    break
            for k in delete_keys:
                del store[k]
            return MockDeleteResult(deleted_count=len(delete_keys))

        async def create_index(self, *args, **kwargs):
            return "mock_index"
    
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
    
    users_mock = InMemoryCollection("users")
    carts_mock = InMemoryCollection("carts")
    items_mock = InMemoryCollection("items")
    feedback_mock = InMemoryCollection("feedback")
    
    # Import the modules to patch them (new structure)
    import app.core.security as security_module
    import app.core.dependencies as deps_module
    import app.core.database as db_module
    import app.repositories.user_repository as user_repo_module
    import app.repositories.cart_repository as cart_repo_module
    import app.repositories.item_repository as item_repo_module
    import app.repositories.feedback_repository as feedback_repo_module
    
    # CRITICAL: Patch where functions are USED (dependencies module)
    # Python creates references when importing, so we must patch the reference
    # in dependencies.py, not just the original in security.py
    # We patch both places to be safe, but the dependencies patch is the critical one
    # Also patch users_collection in security_module since get_or_create_user_from_token uses it
    with patch.object(deps_module, "verify_auth0_token", new=mock_verify_token):
        with patch.object(deps_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
            # Also patch at source for completeness (any direct imports elsewhere)
            with patch.object(security_module, "verify_auth0_token", new=mock_verify_token):
                with patch.object(security_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
                    # Patch database collections - must patch in all modules that import them
                    with patch.object(db_module, "users_collection", users_mock):
                        with patch.object(db_module, "carts_collection", carts_mock):
                            with patch.object(db_module, "items_collection", items_mock):
                                with patch.object(db_module, "feedback_collection", feedback_mock):
                                    # Also patch in security_module since it imports users_collection
                                    with patch.object(security_module, "users_collection", users_mock):
                                        with patch.object(deps_module, "users_collection", users_mock):
                                            # Patch in repository modules since they import collections at module level
                                            with patch.object(user_repo_module, "users_collection", users_mock):
                                                with patch.object(cart_repo_module, "carts_collection", carts_mock):
                                                    with patch.object(item_repo_module, "items_collection", items_mock):
                                                        with patch.object(feedback_repo_module, "feedback_collection", feedback_mock):
                                                            with TestClient(app) as client:
                                                                auth_headers = {"Authorization": "Bearer mock_token_for_testing"}
                                                                client._auth_headers = auth_headers

                                                                original_get = client.get
                                                                original_post = client.post
                                                                original_put = client.put
                                                                original_delete = client.delete

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
    import app.core.security as security_module
    import app.core.dependencies as deps_module
    
    # Patch where functions are used (dependencies module)
    with patch.object(deps_module, "verify_auth0_token", new=mock_verify_token):
        with patch.object(deps_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
            # Also patch at source
            with patch.object(security_module, "verify_auth0_token", new=mock_verify_token):
                with patch.object(security_module, "get_or_create_user_from_token", new=mock_get_or_create_user):
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


# Mock fixtures for ML services and external dependencies
@pytest.fixture
def mock_openai_parser():
    """Mock OpenAI parser services."""
    with patch('app.services.ai.openai_parser.parse_images_with_openai') as mock_images, \
         patch('app.services.ai.openai_parser.parse_inner_text_with_openai') as mock_text:
        yield {
            'parse_images': mock_images,
            'parse_text': mock_text
        }


@pytest.fixture
def mock_email_service():
    """Mock email sending service."""
    with patch('app.services.email.email_service.send_email_ses') as mock:
        yield mock


@pytest.fixture
def mock_extract_product_name():
    """Mock product name extraction utility."""
    with patch('app.utils.utils.extract_product_name_from_url') as mock:
        yield mock
