"""
Smart Healthcare API Gateway
────────────────────────────
Central entry-point for all client requests.

Responsibilities:
  • JWT verification (delegates to auth-service /auth/verify)
  • Request routing to downstream microservices
  • Rate limiting per IP
  • Structured access logging
  • Health aggregation across services
"""

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis import Redis
from typing import Optional
from decouple import config
import httpx, asyncio
from utils.logger import logger, time

# ================== Service URLs ==================
AUTH_SERVICE_URL    = config("AUTH_SERVICE_URL", default="http://auth-service:8001")
PATIENT_SERVICE_URL = config("PATIENT_SERVICE_URL", default="http://patient-service:8002")

# ================== Request throttling configuration ==================
RATE_LIMIT_REQUESTS = int(config('RATE_LIMIT_REQUESTS', default=100))
RATE_LIMIT_WINDOW_SECONDS = int(config('RATE_LIMIT_WINDOW_SECONDS', default=60))
RATE_LIMIT_EXEMPT_PATHS = set(config('RATE_LIMIT_EXEMPT_PATHS', default='/,/health').split(','))

# ================== Route table ==================
#  Maps path prefix → (target base URL, requires auth)
ROUTE_TABLE: list[tuple[str, str, bool]] = [
    ("/api/v1/auth/health",   AUTH_SERVICE_URL,    False),
    ("/api/v1/auth/register", AUTH_SERVICE_URL,    False),
    ("/api/v1/auth/login",    AUTH_SERVICE_URL,    False),
    ("/api/v1/auth/refresh",  AUTH_SERVICE_URL,    False),
    ("/api/v1/auth/reset-password", AUTH_SERVICE_URL, False),
    ("/api/v1/auth/confirm-password", AUTH_SERVICE_URL, False),
    ("/api/v1/auth/",         AUTH_SERVICE_URL,    True),
    ("/api/v1/users/", AUTH_SERVICE_URL, True),
    ("/api/v1/patients/health", PATIENT_SERVICE_URL, False),
    ("/api/v1/patients",      PATIENT_SERVICE_URL, True),
]

PUBLIC_PATHS = {"/", "/health", "/gateway/health", "/gateway/docs", "/gateway/openapi.json", "/gateway/redoc"}

# ================== App init ==================
app = FastAPI(
    title="SmartHealthCare API Gateway",
    description=(
        "Unified entry-point for the Smart Healthcare platform.\n\n"
        "Routes:\n"
        "- `/api/v1/auth/*` → Auth Service (port 8001)\n"
        "- `/api/v1/users/*` → User Service (port 8001)\n"
        "- `/api/v1/patients/*` → Patient Service (port 8002)\n\n"
        "**All non-public endpoints require `Authorization: Bearer <token>`.**"
    ),
    version="0.0.1",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://gateway-test.shc.kodashub.com", "description": "Test server 1"},
        {"url": "https://gateway-shc.vercel.app", "description": "Test server 2"},
        {"url": "https://gateway.shc.kodashub.com", "description": "Production server"}
    ],
    docs_url="/gateway/docs",
    redoc_url="/gateway/redoc",
    openapi_url="/gateway/openapi.json",
    contact={
        "name": "Peter Oyelegbin",
        "email": "peteroyelegbin@gmail.com",
    },
    license_info={"name": "MIT",},
)


# ================== Create Redis Client ==================
redis_client = Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), password=config('REDIS_PASSWORD'), db=0, decode_responses=True)


# ================== Configure CORS to allow requests from the frontend ==================
app.add_middleware(
    CORSMiddleware, allow_origins=config('ALLOWED_ORIGINS', default='*').split(','),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


# ================== Request throttling configuration ==================
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
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": f"Rate limit exceeded. Try again in {RATE_LIMIT_WINDOW_SECONDS} seconds."})
    return await call_next(request)


# ================== Route resolver ==================
def resolve_route(path: str) -> tuple[Optional[str], bool]:
    """Return (target_base_url, requires_auth) or (None, False) if unmatched."""
    for prefix, target, auth_required in ROUTE_TABLE:
        if path.startswith(prefix):
            return target, auth_required
    return None, False


# ================== Token verification ==================
async def verify_token(auth_header: str, client: httpx.AsyncClient) -> dict:
    """Call the auth-service /auth/verify endpoint and return user payload."""
    try:
        resp = await client.get(f"{AUTH_SERVICE_URL}/auth/verify", headers={"Authorization": auth_header}, timeout=5.0)
    except httpx.RequestError as exc:
        logger.error(f"Auth service unreachable: {exc}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication service is unavailable")
    data = resp.json()
    if not data.get("valid"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=data.get("message", "Invalid or expired token"))
    return data


# ================== Proxy helper ==================
EXCLUDED_REQUEST_HEADERS  = {"host", "content-length", "transfer-encoding"}
EXCLUDED_RESPONSE_HEADERS = {"content-encoding", "transfer-encoding", "connection"}

async def proxy_request(request: Request, target_url: str, client: httpx.AsyncClient, extra_headers: Optional[dict] = None) -> Response:
    """Forward the incoming request to the target service and stream the response back."""
    body = await request.body()

    forward_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in EXCLUDED_REQUEST_HEADERS
    }
    if extra_headers:
        forward_headers.update(extra_headers)

    # Preserve query string
    url = httpx.URL(target_url + request.url.path, params=dict(request.query_params))

    try:
        upstream = await client.request(
            method=request.method, url=url, headers=forward_headers,
            content=body, timeout=30.0
        )
    except httpx.RequestError as exc:
        logger.error(f"Upstream error [{target_url}]: {exc}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Upstream service error: {exc}")

    response_headers = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in EXCLUDED_RESPONSE_HEADERS
    }

    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)


# ================== Middleware ==================
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    user_email = "Anonymous"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        user_email = "Authenticated"

    response = await call_next(request)
    process_time = round(time.time() - start_time, 3)
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "ip": request.client.host if request.client else "unknown",
        "user": user_email,
        "duration": process_time,
    }
    if response.status_code >= 400:
        logger.error(log_data)
    else:
        logger.info(log_data)
    return response


@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    # start_time = time.time()
    client_ip = request.client.host if request.client else "anonymous"
    path = request.url.path

    # Skip gateway's own routes
    if path in PUBLIC_PATHS or path.startswith("/gateway/"):
        return await call_next(request)

    # ================== 2. Route resolution ==================
    target_url, auth_required = resolve_route(path)
    if target_url is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": f"No route found for path: {path}"})

    # ================== 3. Auth check ==================
    extra_headers: dict = {}
    if auth_required:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Authorization header missing or malformed"})
        async with httpx.AsyncClient() as client:
            try:
                user_data = await verify_token(auth_header, client)
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        # Forward verified user context to downstream services
        extra_headers = {
            "X-User-Id":   str(user_data.get("user_id", "")),
            "X-Username":  user_data.get("username", ""),
            "X-Is-Admin": user_data.get("is_admin", False),
            "X-Forwarded-For": client_ip,
        }

    # ================== 4. Proxy ==================
    async with httpx.AsyncClient() as client:
        try:
            response = await proxy_request(request, target_url, client, extra_headers)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return response


# ================== Gateway routes ==================
@app.get("/", tags=["Gateway"])
def root():
    return {
        "service": "Smart Healthcare API Gateway",
        "version": "0.0.1",
        "docs": "/gateway/docs",
        "services": {
            "auth":    f"{AUTH_SERVICE_URL}/auth/docs",
            "patient": f"{PATIENT_SERVICE_URL}/patients/docs",
        },
    }

@app.get("/health", tags=["Gateway"])
def health():
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/gateway/health", tags=["Gateway"])
async def gateway_health():
    """
    Aggregate health check — pings every downstream service.
    """
    service_urls = {
        "auth-service":    f"{AUTH_SERVICE_URL}/health",
        "patient-service": f"{PATIENT_SERVICE_URL}/health",
    }
    async def ping(name: str, url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(url)
                return {"service": name, "status": "healthy" if r.status_code == 200 else "degraded", "code": r.status_code}
        except Exception as e:
            return {"service": name, "status": "unreachable", "error": str(e)}
    results = await asyncio.gather(*[ping(n, u) for n, u in service_urls.items()])
    all_healthy = all(r["status"] == "healthy" for r in results)
    return {"gateway": "healthy", "downstream": results, "overall": "healthy" if all_healthy else "degraded"}
