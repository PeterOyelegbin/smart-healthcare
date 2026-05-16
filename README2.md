# 🏥 Smart Healthcare Distributed Services

A production-ready microservices backend for a Smart Healthcare System built with **FastAPI**.

---

## Architecture

```
Client
  │
  ▼
┌─────────────────────────────┐
│       API Gateway :8000     │  ← Single entry-point
│  • JWT verification         │
│  • Rate limiting (100/min)  │
│  • Request routing          │
│  • Health aggregation       │
└────────┬────────────────────┘
         │
    ┌────┴──────────────────┐
    │                       │
    ▼                       ▼
┌───────────────┐   ┌────────────────────┐
│ Auth Service  │   │  Patient Service   │
│   :8001       │   │     :8002          │
│               │   │                    │
│ • Register    │   │ • Patient CRUD     │
│ • Login       │   │ • Medical Records  │
│ • JWT issue   │   │ • Appointments     │
│ • Token       │   │ • Vital Signs      │
│   rotation    │   │ • Role-based access│
│ • Blacklist   │   │                    │
└───────────────┘   └────────────────────┘
```

---

## Services

| Service          | Port | Responsibility                                  |
|------------------|------|-------------------------------------------------|
| `api-gateway`    | 8000 | Routing, auth verification, rate limiting       |
| `auth-service`   | 8001 | User registration, login, JWT tokens            |
| `patient-service`| 8002 | Patients, medical records, appointments, vitals |

---

## Quick Start

### With Docker Compose (recommended)

```bash
git clone <repo>
cd healthcare/

docker-compose up --build
```

Open:
- Gateway docs: http://localhost:8000/gateway/docs
- Auth docs:    http://localhost:8001/auth/docs
- Patient docs: http://localhost:8002/patients/docs

### Without Docker (dev mode)

**Auth Service**
```bash
cd auth-service
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
```

**Patient Service**
```bash
cd patient-service
pip install -r requirements.txt
uvicorn main:app --port 8002 --reload
```

**API Gateway**
```bash
cd api-gateway
pip install -r requirements.txt
AUTH_SERVICE_URL=http://localhost:8001 \
PATIENT_SERVICE_URL=http://localhost:8002 \
uvicorn main:app --port 8000 --reload
```

---

## API Reference

### Auth Service — `/auth/*`

| Method | Path                  | Auth | Description               |
|--------|-----------------------|------|---------------------------|
| POST   | `/auth/register`      | ❌   | Register a new user        |
| POST   | `/auth/login`         | ❌   | Login → JWT tokens         |
| POST   | `/auth/refresh`       | ❌   | Refresh access token       |
| POST   | `/auth/logout`        | ✅   | Revoke token               |
| GET    | `/auth/verify`        | ✅   | Verify token (gateway use) |
| GET    | `/auth/me`            | ✅   | Current user profile       |
| PUT    | `/auth/me/password`   | ✅   | Change password            |
| GET    | `/auth/users`         | ✅   | List users (admin only)    |

### Patient Service — `/patients/*`

| Method | Path                                             | Roles                      |
|--------|--------------------------------------------------|----------------------------|
| POST   | `/patients`                                      | admin, doctor, nurse        |
| GET    | `/patients`                                      | admin, doctor, nurse        |
| GET    | `/patients/{id}`                                 | all roles                   |
| PUT    | `/patients/{id}`                                 | admin, doctor, nurse        |
| DELETE | `/patients/{id}`                                 | admin                       |
| POST   | `/patients/{id}/medical-records`                 | admin, doctor               |
| GET    | `/patients/{id}/medical-records`                 | all roles                   |
| PUT    | `/patients/{id}/medical-records/{rid}`           | admin, doctor               |
| DELETE | `/patients/{id}/medical-records/{rid}`           | admin                       |
| POST   | `/patients/{id}/appointments`                    | admin, doctor, nurse        |
| GET    | `/patients/{id}/appointments`                    | all roles                   |
| PUT    | `/patients/{id}/appointments/{aid}`              | admin, doctor, nurse        |
| DELETE | `/patients/{id}/appointments/{aid}`              | admin, doctor, nurse        |
| POST   | `/patients/{id}/vitals`                          | admin, doctor, nurse        |
| GET    | `/patients/{id}/vitals`                          | all roles                   |
| GET    | `/patients/{id}/vitals/latest`                   | all roles                   |

---

## Authentication Flow

```
1. POST /auth/register   → create account
2. POST /auth/login      → { access_token, refresh_token }
3. GET  /patients/...    → Authorization: Bearer <access_token>
4. POST /auth/refresh    → rotate tokens before expiry
5. POST /auth/logout     → revoke token
```

---

## User Roles

| Role      | Capabilities                                                    |
|-----------|-----------------------------------------------------------------|
| `admin`   | Full access to all resources, user management                   |
| `doctor`  | Create/update patients, medical records, appointments           |
| `nurse`   | Create/update patients, appointments, record vitals             |
| `patient` | View own records, appointments, vitals (non-confidential only)  |

---

## Environment Variables

### Auth Service
| Variable                      | Default                           |
|-------------------------------|-----------------------------------|
| `DATABASE_URL`                | `sqlite:///./auth.db`             |
| `SECRET_KEY`                  | (change in production!)           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                              |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                               |

### Patient Service
| Variable       | Default                    |
|----------------|----------------------------|
| `DATABASE_URL` | `sqlite:///./patients.db`  |

### API Gateway
| Variable               | Default                         |
|------------------------|---------------------------------|
| `AUTH_SERVICE_URL`     | `http://auth-service:8001`      |
| `PATIENT_SERVICE_URL`  | `http://patient-service:8002`   |
| `RATE_LIMIT_REQUESTS`  | `100`                           |
| `RATE_LIMIT_WINDOW`    | `60` (seconds)                  |

---

## Production Checklist

- [ ] Replace SQLite with PostgreSQL for each service
- [ ] Set a strong `SECRET_KEY` (32+ random characters)
- [ ] Enable HTTPS via a reverse proxy (Nginx / Traefik)
- [ ] Restrict `ALLOWED_ORIGINS` to your frontend domain
- [ ] Add Redis for distributed rate limiting
- [ ] Add Prometheus + Grafana for observability
- [ ] Set up CI/CD pipeline
- [ ] Store secrets in Vault / AWS Secrets Manager
