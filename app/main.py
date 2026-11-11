from fastapi import FastAPI

from app.api.endpoints import jobs
from app.api.endpoints.auth import router as auth_router


# Initialize the FastAPI application.
app = FastAPI(
    title="DevJob Radar",
    description="Personal job aggregator and application tracker",
    version="0.1.0",
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# Register the jobs router.
# All job endpoints will start with /api/v1.
app.include_router(
    jobs.router,
    prefix="/api/v1",
)


# Return a welcome message.
@app.get("/")
def root():
    return {
        "message": "Welcome to DevJob Radar"
    }


# Check if the application is running.
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
