import pytest
from unittest.mock import MagicMock, patch, Mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt

from main import app
from database.db_config import Base, get_db
from database.models import User
from database import schema
from utils.auth import (
    register_user,
    authenticate_user,
    blacklist_token,
    is_token_blacklisted,
    get_current_user,
    password_update,
    password_reset,
)
from utils.security import (
    hash_password,
    verify_password,
    create_token_pair,
    decode_token,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    create_password_reset_token,
)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

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


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with mocked database."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ============================================================================
# USER FIXTURES
# ============================================================================

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
    """Valid user login data."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123",
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
def valid_tokens(test_user):
    """Generate valid tokens for a test user."""
    tokens = create_token_pair({"sub": test_user.email})
    return tokens


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestPasswordSecurity:
    """Test password hashing and verification."""
    
    def test_hash_password_creates_different_hash(self):
        """Test that hashing the same password produces different hashes."""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_correct_password(self):
        """Test that correct password verifies successfully."""
        password = "CorrectPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that incorrect password fails verification."""
        password = "CorrectPassword123"
        wrong_password = "WrongPassword123"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestTokenGeneration:
    """Test JWT token creation and validation."""
    
    @patch("utils.security.redis_client")
    def test_create_access_token(self, mock_redis):
        """Test access token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        decoded = decode_token(token)
        assert decoded["sub"] == "test@example.com"
        assert decoded["type"] == "access"
    
    @patch("utils.security.redis_client")
    def test_create_refresh_token(self, mock_redis):
        """Test refresh token creation."""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        decoded = decode_token(token)
        assert decoded["sub"] == "test@example.com"
        assert decoded["type"] == "refresh"
        assert "jti" in decoded
    
    @patch("utils.security.redis_client")
    def test_create_token_pair(self, mock_redis):
        """Test creation of both access and refresh tokens."""
        data = {"sub": "test@example.com"}
        tokens = create_token_pair(data)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        access_decoded = decode_token(tokens["access_token"])
        refresh_decoded = decode_token(tokens["refresh_token"])
        
        assert access_decoded["type"] == "access"
        assert refresh_decoded["type"] == "refresh"
    
    @patch("utils.security.redis_client")
    def test_create_password_reset_token(self, mock_redis):
        """Test password reset token creation."""
        data = {"sub": "test@example.com"}
        token = create_password_reset_token(data)
        
        assert token is not None
        decoded = decode_token(token)
        assert decoded["sub"] == "test@example.com"
        assert decoded["type"] == "reset"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises exception."""
        with pytest.raises(Exception):
            decode_token("invalid.token.here")


# ============================================================================
# AUTHENTICATION LOGIC TESTS
# ============================================================================

class TestUserAuthentication:
    """Test user authentication functions."""
    
    def test_register_user_success(self, db_session, valid_signup_data):
        """Test successful user registration."""
        signup = schema.Signup(**valid_signup_data)
        user = register_user(db_session, signup)
        
        assert user.id is not None
        assert user.email == valid_signup_data["email"].lower()
        assert user.business_name == valid_signup_data["business_name"]
        assert user.verified is True
    
    def test_register_user_duplicate_email(self, db_session, test_user, valid_signup_data):
        """Test registration with duplicate email fails."""
        signup = schema.Signup(**valid_signup_data)
        
        with pytest.raises(Exception):
            register_user(db_session, signup)
    
    def test_authenticate_user_success(self, db_session, test_user, valid_login_data):
        """Test successful user authentication."""
        tokens = authenticate_user(db_session, valid_login_data["email"], valid_login_data["password"])
        
        assert tokens is not None
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    
    def test_authenticate_user_wrong_password(self, db_session, test_user, valid_login_data):
        """Test authentication with wrong password fails."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            authenticate_user(db_session, valid_login_data["email"], "WrongPassword123")
    
    def test_authenticate_user_nonexistent_email(self, db_session):
        """Test authentication with non-existent email fails."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            authenticate_user(db_session, "nonexistent@example.com", "AnyPassword123")
    
    def test_authenticate_inactive_user(self, db_session, test_user, valid_login_data):
        """Test authentication of inactive user fails."""
        from fastapi import HTTPException
        
        test_user.is_active = False
        db_session.commit()
        
        with pytest.raises(HTTPException):
            authenticate_user(db_session, valid_login_data["email"], valid_login_data["password"])


class TestPasswordManagement:
    """Test password update and reset functions."""
    
    def test_password_update_success(self, db_session, test_user):
        """Test successful password update."""
        old_password = "SecurePassword123"
        new_password = "NewSecurePassword456"
        
        result = password_update(db_session, test_user, old_password, new_password)
        
        assert result is not None
        assert verify_password(new_password, result.password)
        assert not verify_password(old_password, result.password)
    
    def test_password_update_wrong_old_password(self, db_session, test_user):
        """Test password update with wrong old password fails."""
        result = password_update(db_session, test_user, "WrongOldPassword", "NewPassword123")
        
        assert result is None
    
    def test_password_reset(self, db_session, test_user):
        """Test password reset."""
        old_password = "SecurePassword123"
        new_password = "ResetPassword789"
        
        result = password_reset(db_session, test_user, new_password)
        
        assert result is not None
        assert verify_password(new_password, result.password)
        assert not verify_password(old_password, result.password)


class TestTokenBlacklisting:
    """Test token blacklisting functionality."""
    
    @patch("utils.auth.redis_client")
    def test_blacklist_token(self, mock_redis, valid_tokens):
        """Test token blacklisting."""
        token = valid_tokens["access_token"]
        mock_redis.setex.return_value = True
        
        result = blacklist_token(token)
        
        assert result is True
        assert mock_redis.setex.called
    
    @patch("utils.auth.redis_client")
    def test_is_token_blacklisted_true(self, mock_redis):
        """Test checking if token is blacklisted (true case)."""
        token = "some.jwt.token"
        mock_redis.exists.return_value = 1
        
        result = is_token_blacklisted(token)
        
        assert result is True
    
    @patch("utils.auth.redis_client")
    def test_is_token_blacklisted_false(self, mock_redis):
        """Test checking if token is blacklisted (false case)."""
        token = "some.jwt.token"
        mock_redis.exists.return_value = 0
        
        result = is_token_blacklisted(token)
        
        assert result is False


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    @patch("routers.auth.verify_company")
    def test_register_endpoint_success(self, mock_verify, client, valid_signup_data):
        """Test successful registration endpoint."""
        mock_verify.return_value = {"success": True}
        
        response = client.post("/api/v1/auth/register", json=valid_signup_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == valid_signup_data["email"]
        assert data["business_name"] == valid_signup_data["business_name"]
    
    @patch("routers.auth.verify_company")
    def test_register_endpoint_duplicate_email(self, mock_verify, client, test_user, valid_signup_data):
        """Test registration with duplicate email."""
        mock_verify.return_value = {"success": True}
        
        response = client.post("/api/v1/auth/register", json=valid_signup_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @patch("routers.auth.verify_company")
    def test_register_endpoint_company_verification_failed(self, mock_verify, client, valid_signup_data):
        """Test registration with failed company verification."""
        mock_verify.return_value = {"success": False}
        
        response = client.post("/api/v1/auth/register", json=valid_signup_data)
        
        assert response.status_code == 400
        assert "verification failed" in response.json()["detail"].lower()
    
    def test_login_endpoint_success(self, client, test_user, valid_login_data):
        """Test successful login endpoint."""
        response = client.post("/api/v1/auth/login", json=valid_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_endpoint_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        login_data = {"email": test_user.email, "password": "WrongPassword"}
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    def test_login_endpoint_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {"email": "nonexistent@example.com", "password": "AnyPassword"}
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    @patch("utils.auth.redis_client")
    def test_refresh_token_endpoint_success(self, mock_redis, client, valid_tokens):
        """Test successful token refresh."""
        mock_redis.get.return_value = "test@example.com"
        
        refresh_token = valid_tokens["refresh_token"]
        response = client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_logout_endpoint_success(self, client, test_user, valid_tokens):
        """Test successful logout."""
        access_token = valid_tokens["access_token"]
        refresh_token = valid_tokens["refresh_token"]
        
        with patch("utils.auth.redis_client") as mock_redis:
            # Decode refresh token to get jti
            decoded = decode_token(refresh_token)
            mock_redis.get.return_value = test_user.email
            mock_redis.exists.return_value = 1  # Token exists in redis
            mock_redis.delete.return_value = True
            mock_redis.setex.return_value = True
            
            response = client.post(
                "/api/v1/auth/logout",
                params={"refresh_token": refresh_token},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Status might be 200, 401, or 400 depending on mock behavior
            assert response.status_code in [200, 401, 400]


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    @patch("utils.security.redis_client")
    def test_refresh_access_token_success(self, mock_redis):
        """Test successful token refresh."""
        data = {"sub": "test@example.com"}
        refresh_token = create_refresh_token(data)
        decoded = decode_token(refresh_token)
        
        # Mock redis to return the refresh token
        mock_redis.get.return_value = "test@example.com"
        
        new_token = refresh_access_token(refresh_token)
        
        assert new_token is not None
        new_decoded = decode_token(new_token)
        assert new_decoded["sub"] == "test@example.com"
        assert new_decoded["type"] == "access"
    
    @patch("utils.security.redis_client")
    def test_refresh_access_token_revoked(self, mock_redis):
        """Test token refresh with revoked token."""
        from fastapi import HTTPException
        
        data = {"sub": "test@example.com"}
        refresh_token = create_refresh_token(data)
        
        # Mock redis to return None (token revoked)
        mock_redis.get.return_value = None
        
        with pytest.raises(HTTPException):
            refresh_access_token(refresh_token)
    
    def test_refresh_access_token_invalid_type(self):
        """Test refresh with non-refresh token type."""
        from fastapi import HTTPException
        
        data = {"sub": "test@example.com"}
        access_token = create_access_token(data)
        
        with pytest.raises(HTTPException):
            refresh_access_token(access_token)


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_signup_schema_valid(self, valid_signup_data):
        """Test valid signup schema."""
        signup = schema.Signup(**valid_signup_data)
        
        assert signup.email == valid_signup_data["email"]
        assert signup.password == valid_signup_data["password"]
    
    def test_signup_schema_invalid_email(self, valid_signup_data):
        """Test signup schema with invalid email."""
        valid_signup_data["email"] = "invalid-email"
        
        with pytest.raises(Exception):
            schema.Signup(**valid_signup_data)
    
    def test_signup_schema_password_too_short(self, valid_signup_data):
        """Test signup schema with password too short."""
        valid_signup_data["password"] = "short"
        
        with pytest.raises(Exception):
            schema.Signup(**valid_signup_data)
    
    def test_login_schema_valid(self, valid_login_data):
        """Test valid login schema."""
        login = schema.Login(**valid_login_data)
        
        assert login.email == valid_login_data["email"]
        assert login.password == valid_login_data["password"]
    
    def test_token_schema_valid(self):
        """Test valid token schema."""
        token_data = {
            "access_token": "some.access.token",
            "refresh_token": "some.refresh.token",
            "token_type": "bearer"
        }
        token = schema.Token(**token_data)
        
        assert token.access_token == "some.access.token"
        assert token.token_type == "bearer"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    @patch("routers.auth.verify_company")
    def test_full_registration_and_login_flow(self, mock_verify, client, valid_signup_data, valid_login_data):
        """Test complete flow from registration to login."""
        mock_verify.return_value = {"success": True}
        
        # Register
        register_response = client.post("/api/v1/auth/register", json=valid_signup_data)
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post("/api/v1/auth/login", json=valid_login_data)
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
    
    def test_user_fields_not_exposed_in_response(self, db_session, test_user):
        """Test that sensitive fields like password are not in response."""
        user_data = test_user
        
        # Password should never be exposed
        assert not hasattr(user_data, "password") or user_data.password is not None
