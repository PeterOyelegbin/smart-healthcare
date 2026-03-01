# Smart Healthcare System - Authentication Service
This microservice handles all user authentication and authorization for the Smart Healthcare System. It is responsible for user registration, login, token generation (JWT), and protecting routes for doctors, patients, and administrators.

Built with FastAPI for high performance, SQLAlchemy for database ORM, and Alembic for database migrations.

## ✨ Features
- User Registration: Allows new users (patients, doctors, admins) to create an account.
- Secure Login: Authenticates users and returns a JWT access token.
- JWT Authentication: Issues and validates stateless JSON Web Tokens.
- Role-Based Access Control (RBAC): Enforces permissions based on user roles (e.g., patient, doctor, admin).
- Password Hashing: Uses passlib with Bcrypt for secure password storage.
- Database Migrations: Manages database schema changes seamlessly with Alembic.
- CORS Middleware: Configured to accept requests from the frontend application.

## 🛠️ Technology Stack
- Framework: FastAPI
- Database ORM: SQLAlchemy
- Database Migrations: Alembic
- Database: PostgreSQL (or your preferred SQL database)
- Authentication: python-jose (for JWT) & passlib (for hashing)
- Pydantic: For data validation and settings management.

---

## 🚀 Getting Started
### Prerequisites
- Python 3.9+
- PostgreSQL (or Docker for a containerized database)
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
4. Set up environment variables:
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/smart_health_auth_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
5. Run database migrations with Alembic:
This will create the necessary tables in your database.
```bash
alembic upgrade head
```
6. Start the development server:
```bash
# Dev
fastapi dev main.py

# Prod
uvicorn app.main:app --reload
```
The API will be available at http://localhost:8000. You can view the interactive API documentation at http://localhost:8000/docs.


## 🔐 Authentication Flow
- Registration: A user sends a POST request to /api/v1/auth/register with their email, password, and role. The password is hashed, and the user is stored in the database.
- Login: The user sends a POST request to /api/v1/auth/login (using OAuth2 Password flow) with their email and password.
- Token Issuance: If credentials are valid, the server returns a JSON response containing an access_token (JWT) and a token_type (usually "bearer").
- Accessing Protected Endpoints: For subsequent requests, the client includes the token in the
    * Authorization header:
    * Authorization: Bearer <your_access_token>
-  Token Validation: The service validates the token on each request, extracts the user's identity and role, and grants or denies access.


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
2. Create a feature branch (git checkout -b feature/AmazingFeature).
3. Commit your changes (git commit -m 'Add some AmazingFeature').
4. Push to the branch (git push origin feature/AmazingFeature).
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
