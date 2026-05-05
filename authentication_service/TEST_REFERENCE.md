# 🧪 Test Quick Reference

## Running Tests

```bash
# All tests
./.venv/bin/python -m pytest tests/test_auth.py -v

# With coverage
./.venv/bin/python -m pytest tests/test_auth.py --cov=. --cov-report=html

# Specific test class
./.venv/bin/python -m pytest tests/test_auth.py::TestPasswordSecurity -v

# Specific test
./.venv/bin/python -m pytest tests/test_auth.py::TestPasswordSecurity::test_hash_password_creates_different_hash -v

# Tests matching pattern
./.venv/bin/python -m pytest -k "register" -v

# Stop on first failure
./.venv/bin/python -m pytest tests/test_auth.py -x

# With shell script
./run_tests.sh all
./run_tests.sh coverage
./run_tests.sh unit
```

## Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestPasswordSecurity` | 3 | Hash, verify passwords |
| `TestTokenGeneration` | 5 | Create, validate, decode tokens |
| `TestUserAuthentication` | 6 | Register, login, authenticate |
| `TestPasswordManagement` | 3 | Update, reset passwords |
| `TestTokenBlacklisting` | 3 | Blacklist, check tokens |
| `TestAuthEndpoints` | 8 | API endpoints |
| `TestTokenRefresh` | 3 | Refresh token logic |
| `TestSchemaValidation` | 5 | Pydantic models |
| `TestAuthenticationFlow` | 2 | End-to-end flows |

## Available Fixtures

```python
# Database & Client
db_session          # In-memory SQLite session
client              # FastAPI test client

# Users
test_user           # Regular user (test@example.com)
admin_user          # Admin user
inactive_user       # Inactive user
another_user_data   # Another user's data

# Data
valid_signup_data   # Registration data
valid_login_data    # Login credentials
valid_tokens        # JWT tokens

# Mocks
mock_redis          # Mocked Redis client
mock_verify_company # Mocked company verification
```

## Coverage Report

```bash
# Terminal report
./.venv/bin/python -m pytest tests/test_auth.py --cov=. --cov-report=term-missing

# HTML report (opens in browser)
./.venv/bin/python -m pytest tests/test_auth.py --cov=. --cov-report=html
open htmlcov/index.html
```

## Common Test Patterns

### Test a successful operation
```python
def test_operation_success(self, fixture):
    """Test successful operation."""
    result = do_something(fixture)
    assert result is not None
```

### Test error handling
```python
def test_operation_error(self, fixture):
    """Test error handling."""
    with pytest.raises(SomeException):
        do_something_invalid(fixture)
```

### Test with mocking
```python
def test_with_mock(self, fixture):
    """Test with mocked external service."""
    with patch("module.service") as mock_service:
        mock_service.return_value = expected_value
        result = function_using_service()
        assert result == expected_value
```

## Test Statistics

- **Total Tests**: 38
- **Pass Rate**: 100%
- **Execution Time**: ~4.7 seconds
- **Coverage**: 75% overall, 98% auth module
- **Python Version**: 3.9.25
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Auth**: JWT with Argon2 password hashing

## Debugging Tips

### Run with detailed output
```bash
./.venv/bin/python -m pytest tests/test_auth.py -vv --tb=long
```

### Show print statements
```bash
./.venv/bin/python -m pytest tests/test_auth.py -v -s
```

### Stop on first failure with debugger
```bash
./.venv/bin/python -m pytest tests/test_auth.py -x --pdb
```

### Run specific markers
```bash
./.venv/bin/python -m pytest -m "unit" -v
./.venv/bin/python -m pytest -m "security" -v
```

## Dependencies

Install via:
```bash
pip install -r requirements.txt
```

Or individually:
```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

## File Structure

```
authentication_service/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_auth.py          # Main tests (38 cases)
│   └── README.md             # Testing docs
├── pytest.ini                # Pytest config
├── run_tests.sh              # Test runner
├── TESTING.md                # Testing guide
└── requirements.txt          # Dependencies
```

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=. --cov-report=xml --junitxml=results.xml
```

---

**Last Updated**: May 2, 2026  
**Status**: ✅ All 38 tests passing  
**Coverage**: 75% (98% auth module)
