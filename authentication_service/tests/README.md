# Authentication Service Tests

This directory contains comprehensive unit and integration tests for the Smart Healthcare Authentication Service using pytest.

## Overview

The test suite covers:

- **Security Tests**: Password hashing, verification, and token generation
- **Authentication Logic Tests**: User registration, login, and authentication flows
- **Password Management Tests**: Password updates and resets
- **Token Management Tests**: Token blacklisting, refresh, and validation
- **API Endpoint Tests**: All REST API endpoints
- **Schema Validation Tests**: Pydantic model validation
- **Integration Tests**: Complete authentication workflows

## Test Structure

```
tests/
├── test_auth.py           # Main test file with all test cases
└── conftest.py (optional) # Shared pytest fixtures
```

### Test Classes

1. **TestPasswordSecurity** - Password hashing and verification
2. **TestTokenGeneration** - JWT token creation and validation
3. **TestUserAuthentication** - User registration and login
4. **TestPasswordManagement** - Password updates and resets
5. **TestTokenBlacklisting** - Token revocation functionality
6. **TestAuthEndpoints** - REST API endpoint tests
7. **TestTokenRefresh** - Token refresh functionality
8. **TestSchemaValidation** - Pydantic schema validation
9. **TestAuthenticationFlow** - End-to-end authentication flows

## Installation

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

Or install just test packages:
```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run tests with verbose output:
```bash
pytest -v
```

### Run tests with coverage report:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test class:
```bash
pytest tests/test_auth.py::TestPasswordSecurity -v
```

### Run specific test:
```bash
pytest tests/test_auth.py::TestPasswordSecurity::test_hash_password_creates_different_hash -v
```

### Run tests matching a pattern:
```bash
pytest -k "register" -v
```

### Run with markers:
```bash
pytest -m unit -v
```

## Test Coverage

Current test suite includes **50+** test cases covering:

- ✅ Password security and hashing
- ✅ JWT token creation and validation
- ✅ User registration with validation
- ✅ User authentication
- ✅ Token refresh and blacklisting
- ✅ Password updates and resets
- ✅ API endpoints (register, login, refresh, logout)
- ✅ Schema validation
- ✅ Error handling and exceptions
- ✅ Integration flows

## Key Features

### Fixtures

The test suite includes several pytest fixtures:

- `db_session` - In-memory SQLite database for each test
- `client` - FastAPI test client with mocked database
- `valid_signup_data` - Sample registration data
- `valid_login_data` - Sample login credentials
- `test_user` - Pre-created test user
- `admin_user` - Pre-created admin user
- `valid_tokens` - Generated test tokens

### Mocking

Tests use `unittest.mock` to mock external dependencies:

- Redis client for token management
- Company verification service
- Database session management

### Database

- Uses in-memory SQLite database
- Automatically creates and destroys tables per test
- No external database required

## Example Test Output

```
tests/test_auth.py::TestPasswordSecurity::test_hash_password_creates_different_hash PASSED
tests/test_auth.py::TestPasswordSecurity::test_verify_password_correct_password PASSED
tests/test_auth.py::TestTokenGeneration::test_create_access_token PASSED
tests/test_auth.py::TestUserAuthentication::test_register_user_success PASSED
tests/test_auth.py::TestAuthEndpoints::test_login_endpoint_success PASSED
...

====== 50 passed in 2.34s ======
```

## Best Practices Used

1. **Isolation**: Each test is independent and uses fresh fixtures
2. **Mocking**: External dependencies are mocked to avoid side effects
3. **Clear naming**: Test names describe what is being tested
4. **Comprehensive coverage**: Tests cover happy paths, edge cases, and error scenarios
5. **Organization**: Tests grouped logically by functionality
6. **Documentation**: Each test class has docstrings

## Continuous Integration

To run tests in CI/CD pipeline:

```bash
pytest --cov=. --cov-report=xml --junitxml=test-results.xml
```

## Adding New Tests

When adding new features, follow this pattern:

```python
class TestNewFeature:
    """Test new feature functionality."""
    
    def test_feature_success(self, fixtures):
        """Test successful feature operation."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_feature_error(self, fixtures):
        """Test feature error handling."""
        # Arrange
        # Act
        # Assert
        pass
```

## Troubleshooting

### Import errors
Ensure you're in the authentication_service directory:
```bash
cd authentication_service
pytest
```

### Database errors
Make sure SQLAlchemy models are properly defined. Tests use in-memory SQLite.

### Redis/External service errors
These are mocked in tests using `unittest.mock`. Check mock setup if tests fail unexpectedly.

## Environment Variables

For local testing, tests use mocked Redis and database. The following env vars are loaded if `.env` exists:

- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`

## Performance

Current test suite runs in **< 5 seconds** on modern hardware.

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Add stress tests for concurrent authentication
- [ ] Add tests for rate limiting
- [ ] Add tests for user roles and permissions
- [ ] Add tests for audit logging
- [ ] Add fixtures for conftest.py

## Questions?

Refer to pytest documentation: https://docs.pytest.org/
