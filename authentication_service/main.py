from fastapi import FastAPI, Request
from routers import auth, users, admin
from utils.security import decode_access_token
from utils.logger import time, logger

# initialize the application
app = FastAPI(
    title="Smart Healthcare Authentication Service - FastAPI",
    description="Authentication service for managing user authentication and authorization",
    version="0.0.1",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://authservice-test.smarthealthcare.com", "description": "Test server"},
        {"url": "https://authservice.smarthealthcare.com", "description": "Production server"}
    ],
    # root_path="/api/v1",
    # root_path_in_servers=True,
    # openapi_url="/docs",
    contact={
        "name": "Peter Oyelegbin",
        "email": "peteroyelegbin@gmail.com",
    },
    license_info={"name": "MIT",},
)


# Log all requests automatically using middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    user_email = "Anonymous"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            user_email = decode_access_token(token)
        except Exception:
            user_email = "Authentication Failed"
    response = await call_next(request)
    process_time = round(time.time() - start_time, 3)
    
    log_data = {"method": request.method, "path": request.url.path, "status_code": response.status_code,
        "ip": request.client.host, "user": user_email, "duration": process_time
    }

    if response.status_code >= 400:
        logger.error(log_data)
    else:
        logger.info(log_data)
    return response


# Health check endpoint
@app.get("/", tags=["Health"])
async def home():
    return {"message": "Authentication service is running"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "authentication", "version": "0.0.1"}

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
