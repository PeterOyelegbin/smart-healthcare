import sys
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.db_config import Base, engine, redis_client
from utils.logger import logger, time
from decouple import config
from routers import patients


# initialize the application
app = FastAPI(
    title="Smart Health Care (Patient Service) - FastAPI",
    description="Patient service for managing patient records and information",
    version="0.0.1",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://patientservice-test.shc.kodashub.com", "description": "Test server 1"},
        {"url": "https://smarthealthcare-five.vercel.app", "description": "Test server 2"},
        {"url": "https://patientservice-shc.vercel.app", "description": "Test server 3"},
        {"url": "https://patientservice.shc.kodashub.com", "description": "Production server"}
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


# ================== Ensure database tables exist before handling requests ==================
@app.on_event("startup")
def on_startup():
    from database import models
    Base.metadata.create_all(bind=engine)


# ================== Configure CORS to allow requests from the frontend ==================
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:8000", "https://shc.kodashub.com", "https://www.shc.kodashub.com"],
    allow_methods=["*"], allow_headers=["*"],
)


# ================== Request throttling configuration ==================
RATE_LIMIT_REQUESTS = int(config('RATE_LIMIT_REQUESTS', default=100))
RATE_LIMIT_WINDOW_SECONDS = int(config('RATE_LIMIT_WINDOW_SECONDS', default=60))
RATE_LIMIT_EXEMPT_PATHS = set(config('RATE_LIMIT_EXEMPT_PATHS', default='/,/health').split(','))

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in RATE_LIMIT_EXEMPT_PATHS:
        return await call_next(request)
    client_ip = request.client.host if request.client else "anonymous"
    key = f"rate_limit:{client_ip}"
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, RATE_LIMIT_WINDOW_SECONDS)
    except Exception as e:
        # If Redis is unavailable, allow requests rather than fail the app
        logger.error(f"Redis error in rate limit: {str(e)}")
        return await call_next(request)
    if count > RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": f"Rate limit exceeded. Try again in {RATE_LIMIT_WINDOW_SECONDS} seconds."},
        )
    return await call_next(request)


# ================== Log all requests automatically using middleware ==================
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    user_email = "Anonymous"
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     try:
    #         user_email = decode_token(token).get("sub")
    #     except Exception:
    #         user_email = "Authentication Failed"
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


# ================== Routes and endpoints go here ==================
# Health check endpoint
@app.get("/", tags=["Health"])
async def home():
    return {"message": "Patient service is running"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "patient", "version": "0.0.1"}

# Include all routers
app.include_router(patients.router)
