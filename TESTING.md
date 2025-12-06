# BuyHive Backend Testing Guide

## Overview

This project includes a comprehensive test suite using **pytest** with proper fixtures, mocking, and test organization. The tests follow industry best practices and are structured like a production application.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and test configuration
├── test_auth.py         # Authentication endpoint tests
├── test_carts.py        # Cart management tests
├── test_items.py        # Item management tests
└── test_security.py     # Security and validation tests
```

## Installation

First, install the test dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting

## Running Tests

### Run All Tests
```bash
pytest
```

Or use the test runner script:
```bash
python run_tests.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestAuthEndpoints::test_get_current_user_authenticated
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

## Test Features

### ✅ What's Tested

1. **Authentication**
   - User authentication with Auth0 tokens
   - Protected endpoint access
   - Invalid token handling
   - Missing token rejection

2. **Cart Management**
   - Creating carts
   - Retrieving carts
   - Editing cart names
   - Deleting carts
   - Input validation

3. **Item Management**
   - Adding items to carts
   - Retrieving items
   - Editing item notes
   - Removing items
   - Input validation

4. **Security**
   - CORS headers
   - Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
   - Authentication requirements
   - Input validation
   - Request size limits

### 🔧 Test Fixtures

The test suite includes several reusable fixtures:

- **`authenticated_client`**: Test client with mocked Auth0 authentication
- **`unauthenticated_client`**: Test client without authentication
- **`sample_cart_data`**: Sample cart data for testing
- **`sample_item_data`**: Sample item data for testing
- **`test_cart`**: Fixture that creates and automatically cleans up a test cart

### 🎭 Mocking

Tests use mocks for:
- **Auth0 token verification**: No need for real Auth0 tokens
- **Database operations**: Tests don't touch your real database
- **External services**: All external calls are mocked

## Writing New Tests

### Example Test Structure

```python
class TestMyFeature:
    """Test suite for my feature."""
    
    def test_feature_success(self, authenticated_client):
        """Test successful feature operation."""
        response = authenticated_client.get("/my-endpoint")
        assert response.status_code == 200
        assert "expected_field" in response.json()
    
    def test_feature_requires_auth(self, unauthenticated_client):
        """Test that feature requires authentication."""
        response = unauthenticated_client.get("/my-endpoint")
        assert response.status_code == 401
```

### Best Practices

1. **Use descriptive test names**: `test_create_cart_success` not `test_cart`
2. **One assertion per test concept**: Test one thing at a time
3. **Clean up test data**: Use fixtures or teardown methods
4. **Test both success and failure cases**: Happy path + error cases
5. **Test authentication**: Always test that protected endpoints require auth

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
```

## Notes

- Tests use **mocked Auth0 tokens** - no real Auth0 setup needed
- Tests **don't touch your real database** - all DB operations are mocked
- Tests are **independent** - each test can run alone
- Tests **clean up after themselves** - no leftover test data

## Troubleshooting

### Tests fail with "Module not found"
Make sure you're in the project root and have installed dependencies:
```bash
pip install -r requirements.txt
```

### Tests fail with database errors
Tests should mock the database. If you see real DB errors, check that mocks are properly set up in `conftest.py`.

### Tests are slow
If tests are slow, you might be hitting real services. Make sure all external calls are mocked.

## Next Steps

- Add integration tests that use a test database
- Add performance/load tests
- Add API contract tests
- Set up CI/CD pipeline

