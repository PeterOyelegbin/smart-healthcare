# Smart Healthcare System - Authentication Service
This microservice handles all user authentication, authorization, and basic user management for the Smart Healthcare System. It is responsible for user registration, login, token generation (JWT), secure token refresh, token blacklisting via Redis, and protecting endpoints based on user roles and status.

Built with FastAPI for high performance, SQLAlchemy for database ORM, and Alembic for database migrations.

## ✨ Features
- **User Registration & Login**: Allows users (system users and admins) to securely register and authenticate.
- **JWT Authentication with Refresh**: Issues stateless access tokens and secure refresh tokens that can be used for session extension.
- **Token Blacklisting**: Integrates with Redis to securely invalidate active tokens upon logout.
- **Role-Based Access Control (RBAC)**: Distinguishes between regular users and top-level admins (`is_admin` flags) dynamically for secured routes.
- **Password Hashing**: Uses `argon2-cffi` for state-of-the-art secure password hashing.
- **Audit Logging**: Custom HTTP middleware that automatically logs request metadata (method, path, status, IP, duration, and user identity) for robust monitoring and auditing.
- **Database Migrations**: Manages database schema changes seamlessly with Alembic.

## 🛠️ Technology Stack
- **Framework**: FastAPI (uvicorn)
- **Database ORM**: SQLAlchemy
- **Database Migrations**: Alembic
- **Database**: SQLite (default configured to `SMC.db`), PostgreSQL compatible.
- **Authentication**: `python-jose` (for JWT) & `argon2-cffi` (for password hashing).
- **Caching & Blacklisting**: Redis container/server for token management.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Redis Server (Must be running for logout/blacklisting features)
- SQLite (or PostgreSQL/MySQL as preferred)
- pip (Python package manager)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/PeterOyelegbin/smart-healthcare.git
cd smart-healthcare/authentication_service
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (`.env`):
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/smart_health_auth_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=1

# Redis Configuration (Required for Token Blacklisting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Check codebase for optional KYC verification APIs configs
```

5. Run database migrations with Alembic:
Setup the application database with its relative schema.
```bash
alembic upgrade head
```

6. Start the development server:
```bash
# Dev environment
fastapi dev main.py

# Prod environment
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API covers multiple environments definitions. Locally, it will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.


## 🔐 Endpoints & Flow

### Health & Monitoring Endpoints
- `GET /` and `GET /health`: Service health checks stating status and version.

### Authentication Endpoints (`/api/v1/auth`)
- `POST /register`: Register a new organization user.
- `POST /login`: Authenticate and receive `access_token` and `refresh_token`.
- `POST /refresh`: Issue a new access token using a valid refresh token.
- `POST /logout`: Logout the user and safely blacklist the access/refresh tokens on Redis.

### Current User Endpoints (`/api/v1/users`)
- `GET /me/profile`: Retrieve the current authenticated user's local profile (`email`, `organisation`, etc).
- `PATCH /me/password-update`: Safely update the logged-in user's password requiring old password verification.

### Administration Endpoints (`/api/v1/users`)
*Requires the authenticated user's `is_admin` parameter to be True.*
- `GET /`: Retrieve all registered users in the system.
- `GET /{user_id}`: Retrieve a specific user by their Unique ID.
- `PATCH /{user_id}/toggle-status`: Activate or deactivate a given user account access.
- `DELETE /{user_id}`: Hard-delete a user locally from the network.

## 🗄️ Database Migrations (Alembic)
This project uses Alembic to manage database schema changes.
- Create a new migration after changing the SQLAlchemy models:
```bash
alembic revision --autogenerate -m "Description of the change"
```
- Apply all pending migrations to the database:
```bash
alembic upgrade head
```
- Rollback the last migration:
```bash
alembic downgrade -1
```

---

## 🤝 Contributing
Contributions are welcome! Please ensure that any new features or bug fixes include appropriate tests and documentation.
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License
This project is licensed under the MIT License.



## Project Initialization
1. Initialize Alembic (run once)
`alembic init alembic`

2. Configure your database URL
```alembic.ini
sqlalchemy.url = sqlite:///./auth.db
```

3. Connect Alembic to your models
```alembic/env.py
from app.database import Base  # adjust import path
target_metadata = Base.metadata
```
