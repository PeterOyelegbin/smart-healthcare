"""
Shared pytest configuration and fixtures for authentication service tests.

This file defines common fixtures and configuration used across all tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from main import app
from database.db_config import Base, get_db
from database.models import User
from utils.security import hash_password


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with mocked database."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("utils.auth.redis_client") as mock:
        with patch("utils.security.redis_client", mock):
            yield mock


@pytest.fixture
def mock_verify_company():
    """Mock company verification service."""
    with patch("utils.compliance.verify_company") as mock:
        mock.return_value = {"success": True}
        yield mock


@pytest.fixture
def valid_signup_data():
    """Valid user signup data."""
    return {
        "business_name": "Test Healthcare Company",
        "registration_number": "REG123456",
        "business_type": ["BUSINESS_NAME"],
        "email": "test@example.com",
        "password": "SecurePassword123",
        "is_consent": True,
    }


@pytest.fixture
def valid_login_data():
    """Valid user login credentials."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123",
    }


@pytest.fixture
def another_user_data():
    """Another user's signup data."""
    return {
        "business_name": "Another Company",
        "registration_number": "REG789012",
        "business_type": ["COMPANY"],
        "email": "another@example.com",
        "password": "AnotherPassword456",
        "is_consent": True,
    }


@pytest.fixture
def test_user(db_session, valid_signup_data):
    """Create a test user in the database."""
    hashed_pw = hash_password(valid_signup_data["password"])
    user = User(
        business_name=valid_signup_data["business_name"],
        registration_number=valid_signup_data["registration_number"],
        email=valid_signup_data["email"].lower(),
        password=hashed_pw,
        is_consent=valid_signup_data["is_consent"],
        verified=True,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin test user."""
    hashed_pw = hash_password("AdminPassword123")
    user = User(
        business_name="Admin Company",
        registration_number="ADMIN123",
        email="admin@example.com",
        password=hashed_pw,
        is_consent=True,
        verified=True,
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    """Create an inactive test user."""
    hashed_pw = hash_password("InactivePassword123")
    user = User(
        business_name="Inactive Company",
        registration_number="INACTIVE123",
        email="inactive@example.com",
        password=hashed_pw,
        is_consent=True,
        verified=True,
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def valid_tokens(test_user):
    """Generate valid tokens for a test user."""
    from utils.security import create_token_pair
    tokens = create_token_pair({"sub": test_user.email})
    return tokens


@pytest.fixture
def expired_token():
    """Generate an expired JWT token."""
    from utils.security import secret_key, algorithm
    from jose import jwt
    
    payload = {
        "sub": "test@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "type": "access"
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


@pytest.fixture
def authorization_header(valid_tokens):
    """Generate authorization header with valid token."""
    return {"Authorization": f"Bearer {valid_tokens['access_token']}"}


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Mark test as a unit test")
    config.addinivalue_line("markers", "integration: Mark test as an integration test")
    config.addinivalue_line("markers", "slow: Mark test as slow running")
    config.addinivalue_line("markers", "security: Mark test as a security test")
    config.addinivalue_line("markers", "endpoint: Mark test as an API endpoint test")
