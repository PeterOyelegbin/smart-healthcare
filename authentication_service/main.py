from fastapi import FastAPI
from routers import auth, users, admin

# initialize the application
app = FastAPI(
    title="Smart Healthcare Authentication Service - FastAPI",
    description="Authentication service for managing user authentication and authorization",
    version="0.0.1",
    # openapi_url="/docs",
    contact={
        "name": "Peter Oyelegbin",
        "email": "peteroyelegbin@gmail.com",
    },
    license_info={"name": "MIT",},
)

# Health check endpoint
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "message": "Authentication service is running"}

@app.get("/health", tags=["Health"])
async def health_check_detailed():
    return {"status": "healthy", "service": "authentication", "version": "0.0.1"}

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
