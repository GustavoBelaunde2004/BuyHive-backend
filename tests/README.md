# BuyHive Backend Tests

This directory contains the test suite for the BuyHive backend API.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── test_auth.py         # Authentication endpoint tests
├── test_carts.py        # Cart management tests
├── test_items.py        # Item management tests
└── test_security.py     # Security and validation tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthEndpoints::test_get_current_user_authenticated
```

### Run with verbose output
```bash
pytest -v
```

## Test Fixtures

- `authenticated_client`: Test client with mocked authentication
- `unauthenticated_client`: Test client without authentication
- `sample_cart_data`: Sample cart data for testing
- `sample_item_data`: Sample item data for testing
- `test_cart`: Fixture that creates and cleans up a test cart

## Writing New Tests

1. Create test files following the pattern `test_*.py`
2. Use the provided fixtures from `conftest.py`
3. Follow the existing test structure with test classes
4. Clean up test data in fixtures or teardown methods

## Notes

- Tests use mocked Auth0 tokens for testing
- Tests should be independent and not rely on each other
- Test data is automatically cleaned up via fixtures
- All protected endpoints are tested for authentication requirements

